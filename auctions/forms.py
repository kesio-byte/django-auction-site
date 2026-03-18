from django import forms
from .models import Listing
from .models import Comment
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name'].strip().title()
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError(f"Category '{name}' already exists.")
        return name

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_starting_bid(self):
        bid = self.cleaned_data.get("starting_bid")
        if bid is not None and bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return bid

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_starting_bid(self):
        bid = self.cleaned_data.get("starting_bid")
        if bid is not None and bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return bid

class BidForm(forms.Form):
    bid = forms.FloatField(
        label="Your Bid",
        min_value=0.01,
        error_messages={
            "required": "Please enter a bid amount.",
            "invalid": "Bid must be a number."
        }
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Add a comment',
                'rows': 3
            }),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if text and len(text.strip()) < 10:   # minimum 10 characters
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        if text and len(text) > 500:          # maximum 500 characters
            raise forms.ValidationError("Comment cannot exceed 500 characters.")
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

