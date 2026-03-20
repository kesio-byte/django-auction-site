from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import User, Category, Listing, Bid, Comment
from django.core.exceptions import ValidationError
from django.contrib import messages


# --- Inline classes for Bids and Comments ---
class BidInline(admin.TabularInline):
    model = Bid
    extra = 1
    fields = ("bidder", "amount")
    show_change_link = True


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ("commenter", "text", "timestamp")
    readonly_fields = ("timestamp",)
    show_change_link = True

<<<<<<< HEAD
# ✅ Category Admin with clickable listing count + duplicate validation
=======

# --- Category Admin with clickable listing count ---
>>>>>>> faa0463 (Refactor migrations and enhance listing form/template)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "listing_count", "image_preview")
    search_fields = ("name",)
    ordering = ("name",)

    def listing_count(self, obj):
<<<<<<< HEAD
        count = obj.listings.count()
=======
        count = obj.listings.count()  # ManyToManyField related_name="listings"
>>>>>>> faa0463 (Refactor migrations and enhance listing form/template)
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

        # 🚫 Starting bid must be positive
        if starting_bid is not None and starting_bid <= 0:
            raise ValidationError("Starting bid must be greater than zero.")

        # 🚫 Active listings must have at least one category
        if active and (not categories or categories.count() == 0):
            raise ValidationError("Active listings must be assigned at least one category.")

        # 🚫 Prevent duplicate categories (ManyToManyField safety)
        if categories and len(categories) != len(set(categories)):
            raise ValidationError("Duplicate categories are not allowed.")

        # 🚫 Optional: limit max categories
        if categories and categories.count() > 3:
            raise ValidationError("A listing cannot have more than 3 categories.")

        return cleaned_data


# --- Listing Admin ---
class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    list_display = ("title", "owner", "starting_bid", "active", "created_at")
    list_filter = ("active", "owner", "categories")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
<<<<<<< HEAD
 
    # Mark created_at as read-only
=======
>>>>>>> faa0463 (Refactor migrations and enhance listing form/template)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Info", {"fields": ("title", "description", "image", "image_url")}),
        ("Auction Details", {"fields": ("starting_bid", "categories", "active")}),
        ("Ownership", {"fields": ("owner", "watchers")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )

    inlines = [BidInline, CommentInline]


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

        # 🚫 Ensure bid is higher than current price
        if listing and amount is not None:
            current_price = listing.starting_bid
            highest_bid = listing.bid_set.order_by("-amount").first()
            if highest_bid:
                current_price = highest_bid.amount

            if amount <= current_price:
                raise ValidationError("Bid must be higher than the current price.")

        # 🚫 Prevent owner from bidding on their own listing
        if listing and bidder == listing.owner:
            raise ValidationError("Owner cannot bid on their own listing.")

        return cleaned_data


# --- Bid Admin ---
class BidAdmin(admin.ModelAdmin):
    form = BidAdminForm
    list_display = ("listing", "bidder", "amount")
    list_filter = ("listing", "bidder")


# --- Comment Admin ---
class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "commenter", "timestamp")
    list_filter = ("listing", "commenter")
    search_fields = ("text",)


# --- Register all models with their Admin classes ---
admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
