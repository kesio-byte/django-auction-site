from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import User, Category, Listing, Bid, Comment
from django.contrib import messages
from django.utils import timezone

# --- Inline classes for Bids and Comments ---
class BidInline(admin.TabularInline):
    model = Bid
    extra = 1
    fields = ("bidder", "amount")
    show_change_link = True


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ("commenter", "description", "timestamp")
    readonly_fields = ("timestamp",)
    show_change_link = True


# ✅ Category Admin with clickable listing count + image preview
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "listing_count", "image_preview")
    search_fields = ("name",)
    ordering = ("name",)

    def listing_count(self, obj):
        count = obj.listings.count()  # ManyToManyField related_name="listings"
        url = (
            reverse("admin:auctions_listing_changelist")
            + f"?categories__id__exact={obj.id}"
        )
        return format_html('<a href="{}">{}</a>', url, count)

    listing_count.short_description = "Number of Listings"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px;" />', obj.image.url)
        return "No image"

    image_preview.short_description = "Thumbnail"


# --- Custom form for Listing validations ---
class ListingAdminForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        categories = cleaned_data.get("categories")
        starting_bid = cleaned_data.get("starting_bid")
        active = cleaned_data.get("active")

        if starting_bid is not None and starting_bid <= 0:
            raise ValidationError("Starting bid must be greater than zero.")

        if active and (not categories or categories.count() == 0):
            raise ValidationError("Active listings must be assigned at least one category.")

        if categories and len(categories) != len(set(categories)):
            raise ValidationError("Duplicate categories are not allowed.")

        if categories and categories.count() > 3:
            raise ValidationError("A listing cannot have more than 3 categories.")

        return cleaned_data

# --- Custom form for Bid validations ---
class BidAdminForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        listing = cleaned_data.get("listing")
        bidder = cleaned_data.get("bidder")
        amount = cleaned_data.get("amount")

        if listing and amount is not None:
            current_price = listing.starting_bid
            highest_bid = listing.bids.order_by("-amount").first()
            if highest_bid:
                current_price = highest_bid.amount

            if amount <= current_price:
                raise ValidationError("Bid must be higher than the current price.")

        if listing and bidder == listing.owner:
            raise ValidationError("Owner cannot bid on their own listing.")

        return cleaned_data

# --- Listing Admin ---
class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    list_display = ("title", "owner", "starting_bid", "active", "created_at", "winner", "final_price")
    actions = ["close_auction", "remove_item"]

    def close_auction(self, request, queryset):
        for listing in queryset:
            highest_bid = listing.bids.order_by("-amount").first()
            if highest_bid:
                listing.winner = highest_bid.bidder
                listing.final_price = highest_bid.amount
            listing.active = False
            listing.closed_at = timezone.now()
            listing.save()
        self.message_user(request, "Selected auctions have been closed.", level=messages.SUCCESS)

    close_auction.short_description = "Close selected auctions"

    def remove_item(self, request, queryset):
        queryset.delete()
        self.message_user(request, "Selected items have been removed.", level=messages.WARNING)

    remove_item.short_description = "Remove selected items"

# --- Bid Admin ---
class BidAdmin(admin.ModelAdmin):
    form = BidAdminForm
    list_display = ("listing", "bidder", "amount")
    list_filter = ("listing", "bidder")


# --- Comment Admin ---
class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "commenter", "timestamp")
    list_filter = ("listing", "commenter")
    search_fields = ("description",)


# --- Register all models with their Admin classes ---
admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
