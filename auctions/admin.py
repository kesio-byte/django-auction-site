from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import User, Category, Listing, Bid, Comment


# ✅ Inline classes for Bids and Comments
class BidInline(admin.TabularInline):
    model = Bid
    extra = 1   # show one empty row for quick adding
    fields = ("bidder", "amount")
    show_change_link = True


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ("commenter", "text", "timestamp")
    readonly_fields = ("timestamp",)
    show_change_link = True


# ✅ Category Admin with clickable listing count
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "listing_count")
    search_fields = ("name",)
    ordering = ("name",)

    def listing_count(self, obj):
        count = obj.listings.count()  # assumes Listing has ForeignKey(Category, related_name="listings")
        url = (
            reverse("admin:auctions_listing_changelist")
            + f"?category__id__exact={obj.id}"
        )
        return format_html('<a href="{}">{}</a>', url, count)

    listing_count.short_description = "Number of Listings"


# ✅ Listing Admin with owner filter + date hierarchy + field grouping + inlines
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "starting_bid", "active", "category", "created_at")
    list_filter = ("active", "category", "owner")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
 
    # 👇 Mark created_at as read-only
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "description", "image")
        }),
        ("Auction Details", {
            "fields": ("starting_bid", "category", "active")
        }),
        ("Ownership", {
            "fields": ("owner", "watchers")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )

    inlines = [BidInline, CommentInline]   #  Inline editing here


# ✅ Bid Admin
class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "bidder", "amount")
    list_filter = ("listing", "bidder")


# ✅ Comment Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "commenter", "timestamp")
    list_filter = ("listing", "commenter")
    search_fields = ("text",)


# ✅ Register all models with their Admin classes
admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
