from django import forms
from .models import Listing, Comment, Category
import re

# ----- Category Form -----
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip().title()
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError(f"Category '{name}' already exists.")
        return name


# ----- Create Listing Form -----
class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'image_url', 'categories', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        if title.isdigit():
            raise forms.ValidationError("Title cannot contain only digits.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()
        if not description:
            raise forms.ValidationError("Description cannot be empty.")
        if description.isdigit():
            raise forms.ValidationError("Description cannot contain only digits.")
        if len(description) < 10:
            raise forms.ValidationError("Description must be at least 10 characters long.")
        return description

    def clean_starting_bid(self):
        bid = self.cleaned_data.get("starting_bid")
        if bid is None or bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return bid

    def clean_categories(self):
        categories = self.cleaned_data.get("categories")
        if not categories or categories.count() == 0:
            raise forms.ValidationError("You must choose at least one category.")
        if categories.count() > 2:
            raise forms.ValidationError("You cannot assign more than 2 categories.")
        category_ids = [c.id for c in categories]
        if len(category_ids) != len(set(category_ids)):
            raise forms.ValidationError("Duplicate categories are not allowed.")
        return categories

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        image_url = cleaned_data.get("image_url")
        if not image and not image_url:
            raise forms.ValidationError("You must provide either an image file or an image URL.")
        if image and image_url:
            raise forms.ValidationError("Provide only one image source: file OR URL, not both.")
        return cleaned_data


# ----- Listing Form (for editing) -----
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'image_url', 'categories', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_starting_bid(self):
        bid = self.cleaned_data.get("starting_bid")
        if bid is None or bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return bid


# ----- Bid Form -----
class BidForm(forms.Form):
    bid = forms.FloatField(
        label="Your Bid",
        min_value=0.01,
        error_messages={
            "required": "Please enter a bid amount.",
            "invalid": "Bid must be a number."
        }
    )


# ----- Comment Form -----
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Add a comment',
                'rows': 3
            }),
        }

    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()
        if description.isdigit():
            raise forms.ValidationError("Comment cannot be only digits.")
        if len(description) < 2:
            raise forms.ValidationError("Comment must be at least 2 characters long.")
        if len(description) > 500:
            raise forms.ValidationError("Comment cannot exceed 500 characters.")
        if not re.match(r'^[A-Za-z0-9\s]+$', description):
            raise forms.ValidationError("Comment cannot contain symbols or special characters.")
        return description
