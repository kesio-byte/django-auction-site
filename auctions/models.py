from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import re

# --- Validation helper for forms ---
def validate_contains_letter(value):
    # Require at least one alphabetic character
    if not re.search(r"[A-Za-z]", value):# ive used regular expression
        raise ValidationError("Must contain at least one letter.")

# ---- Category model with optional image ----
class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to="category_images/", blank=True, null=True)

    def __str__(self):
        return self.name

# ---- User model extending AbstractUser ----
class User(AbstractUser):
    # Extend if needed
    pass

# ---- Listing model ----
# Represents an auction listing with title, description, bids, categories, and lifecycle tracking
class Listing(models.Model):
    # Title validation
    title = models.CharField(
        max_length=64,
        validators=[
            MinLengthValidator(4, "Title must be at least 4 characters."),
            validate_contains_letter
        ]
    )
    description = models.TextField(
        # Description validation
        validators=[
            MinLengthValidator(10, "Description must be at least 10 characters."),
            MaxLengthValidator(1000, "Description cannot exceed 1000 characters.")
        ]
    )
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="listing_images/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField("Category", blank=True, related_name="listings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)

    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_listings")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def current_price(self):
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.amount if highest_bid else self.starting_bid

# ---- Bid model ----
# Represents a single bid placed on a listing, linked to bidder and timestamp
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} by {self.bidder} on {self.listing}"

# ---- Comment model ----
# Represents user comments on listings, with validation and newest-first ordering
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    description = models.TextField(
        # Comment validation
        validators=[
            MinLengthValidator(2, "Comment must be at least 2 characters."),
            MaxLengthValidator(500, "Comment cannot exceed 500 characters.")
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.description.isdigit():
            raise ValidationError("Comment cannot be only digits.")

    def __str__(self):
        return f"Comment by {self.commenter} on {self.listing}"

    class Meta:
        ordering = ['-timestamp']
