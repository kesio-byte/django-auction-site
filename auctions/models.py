from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import re

# --- The the forms validations function ---
def validate_contains_letter(value):
    # Require at least one alphabetic character
    if not re.search(r"[A-Za-z]", value):
        raise ValidationError("Must contain at least one letter.")

# ---- Image model imagefield to category ----
class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to="category_images/", blank=True, null=True)

    def __str__(self):
        return self.name

# ---- User model extending abstractUser ----
class User(AbstractUser):
    # Extend if needed
    pass

# ---- The Listings model Class ---
class Listing(models.Model):
    title = models.CharField(
        max_length=64,
        validators=[
            MinLengthValidator(4, "Title must be at least 4 characters."),
            validate_contains_letter
        ]
    )
    description = models.TextField(
        validators=[
            MinLengthValidator(10, "Description must be at least 10 characters."),
            MaxLengthValidator(1000, "Description cannot exceed 1000 characters.")
        ]
    )
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="listing_images/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)

    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    # ---- Date time created ---
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_listings")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # ---- Date time the auction is closed ----
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):

        # Return the listing title for a human-readable representation in admin and shell
        return self.title

    @property
    def current_price(self):
        highest_bid = self.bids.order_by('-amount').first()

        # Return the hightest bid
        return highest_bid.amount if highest_bid else self.starting_bid

#       ---- Bid model class ----
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)  # captures bid time

    def __str__(self):
        return f"{self.amount} by {self.bidder} on {self.listing}"

# ---- Comment model class ----
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(
        validators=[
            MinLengthValidator(2, "Comment must be at least 2 characters."),
            MaxLengthValidator(500, "Comment cannot exceed 500 characters.")
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.text.isdigit():
            raise ValidationError("Comment cannot be only digits.")

    def __str__(self):
        return f"Comment by {self.commenter} on {self.listing}"

    class Meta:
        ordering = ['-timestamp']
