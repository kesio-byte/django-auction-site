from django import forms
<<<<<<< HEAD
from .models import Listing
from .models import Comment
from .models import Category
import re


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name'].strip().title()
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError(f"Category '{name}' already exists.")
        return name
=======
from .models import Listing, Comment, Category
import re
>>>>>>> faa0463 (Refactor migrations and enhance listing form/template)

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
            # Title input
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            # Description textarea
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            # Starting bid numeric input
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            # Image file upload
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # Image URL input
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            # Categories (ManyToManyField → SelectMultiple)
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            # Active checkbox
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # ----- Title validation -----
    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        if title.isdigit():
            raise forms.ValidationError("Title cannot contain only digits.")
        return title

    # ----- Description validation -----
    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()
        if not description:
            raise forms.ValidationError("Description cannot be empty.")
        if description.isdigit():
            raise forms.ValidationError("Description cannot contain only digits.")
        if len(description) < 10:
            raise forms.ValidationError("Description must be at least 10 characters long.")
        return description

    # ----- Starting bid validation -----
    def clean_starting_bid(self):
        bid = self.cleaned_data.get("starting_bid")
        if bid is None or bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return bid

    # ----- Categories validation -----
    def clean_categories(self):
        categories = self.cleaned_data.get("categories")

        # Must select at least one
        if not categories or categories.count() == 0:
            raise forms.ValidationError("You must choose at least one category.")

        # Limit to 2 (business rule)
        if categories.count() > 2:
            raise forms.ValidationError("You cannot assign more than 2 categories.")

        # Prevent duplicates (though ManyToMany usually collapses them)
        category_ids = [c.id for c in categories]
        if len(category_ids) != len(set(category_ids)):
            raise forms.ValidationError("Duplicate categories are not allowed.")

        return categories

    # ----- Cross-field validation (image vs image_url) -----
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        image_url = cleaned_data.get("image_url")

        # Must provide one image source
        if not image and not image_url:
            raise forms.ValidationError("You must provide either an image file or an image URL.")

        # Cannot provide both
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

<<<<<<< HEAD
=======

>>>>>>> faa0463 (Refactor migrations and enhance listing form/template)
# ----- Comment Form -----
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
<<<<<<< HEAD
        fields = ['description']
=======
        fields = ['text']  # ✅ corrected to match Comment model field name
>>>>>>> faa0463 (Refactor migrations and enhance listing form/template)
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Add a comment',
                'rows': 3
            }),
        }

    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()

        # Rule 1: no digit-only comments
        if description.isdigit():
            raise forms.ValidationError("Comment cannot be only digits.")

        # Rule 2: minimum length
        if len(description) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")

        # Rule 3: no symbols (only letters, numbers, spaces)
        if not re.match(r'^[A-Za-z0-9\s]+$', description):
            raise forms.ValidationError("Comment cannot contain symbols or special characters.")

        return description


    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()

        # Rule 1: no digit-only comments
        if text.isdigit():
            raise forms.ValidationError("Comment cannot be only digits.")

        # Rule 2: minimum length
        if len(text) < 2:
            raise forms.ValidationError("Comment must be at least 2 characters long.")

        # Rule 3: maximum length
        if len(text) > 500:
            raise forms.ValidationError("Comment cannot exceed 500 characters.")

        # Rule 4: no symbols (only letters, numbers, spaces)
        if not re.match(r'^[A-Za-z0-9\s]+$', text):
            raise forms.ValidationError("Comment cannot contain symbols or special characters.")

        return text

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name'].strip().title()
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError(f"Category '{name}' already exists.")
        return name

