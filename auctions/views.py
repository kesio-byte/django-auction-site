from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import User, Listing, Bid, Comment, Category
from .forms import CreateListingForm, BidForm, CommentForm
# --- Unified Listing Detail View ---
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all()
    highest_bid = listing.bids.order_by("-amount").first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid

    # Default forms
    comment_form = CommentForm()
    bid_form = BidForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # --- Handle Bid ---
        if form_type == "bid" and request.user.is_authenticated:
            if not listing.active:
                messages.error(request, "This auction is closed. No more bids allowed.")
            else:
                bid_form = BidForm(request.POST)
                if bid_form.is_valid():
                    amount = bid_form.cleaned_data["bid"]
                    if amount > float(current_price):
                        Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
                        messages.success(request, "Bid placed successfully!")
                    else:
                        messages.error(request, "Bid must be greater than current price.")
                else:
                    messages.error(request, "Invalid bid.")
            return redirect("listing", listing_id=listing.id)

        # --- Handle Comment ---
        elif form_type == "comment" and request.user.is_authenticated:
            if not listing.active:
                messages.error(request, "This auction is closed. No more comments allowed.")
            else:
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.listing = listing
                    comment.commenter = request.user
                    comment.save()
                    messages.success(request, "Comment added.")
                else:
                    # Loop through errors to avoid raw HTML
                    for field, errors in comment_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Invalid comment: {error}")
            return redirect("listing", listing_id=listing.id)

        # --- Handle Watchlist ---
        elif form_type == "watchlist" and request.user.is_authenticated:
            if listing in request.user.watchlist.all():
                request.user.watchlist.remove(listing)
                messages.info(request, "Removed from watchlist.")
            else:
                request.user.watchlist.add(listing)
                messages.success(request, "Added to watchlist.")
            return redirect("listing", listing_id=listing.id)

        # --- Handle Close Auction ---
        elif form_type == "close" and request.user == listing.owner:
            listing.active = False
            listing.closed_at = timezone.now()
            if highest_bid:
                listing.winner = highest_bid.bidder
                listing.final_price = highest_bid.amount
                messages.info(request, f"Auction closed. Winner: {highest_bid.bidder.username}")
            else:
                listing.final_price = listing.starting_bid
                messages.info(request, "Auction closed. No bids were placed.")
            listing.save()
            return redirect("listing", listing_id=listing.id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "current_price": current_price,
        "highest_bid": highest_bid,
        "comment_form": comment_form,
        "form": bid_form
    })





# --- Other Views ---
def categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.active_count = category.listings.filter(active=True).count()
    return render(request, "auctions/categories.html", {"categories": categories})


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(active=True, category=category)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"listings": listings})


@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect("index")
    else:
        form = CreateListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})
    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/register.html")


@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user)
    return render(request, "auctions/my_listings.html", {"listings": listings})


@login_required
def closed_listings(request):
    listings = Listing.objects.filter(active=False)
    return render(request, "auctions/closed_listings.html", {"listings": listings})


@login_required
def my_wins(request):
    listings = Listing.objects.filter(active=False, winner=request.user)
    return render(request, "auctions/my_wins.html", {"listings": listings})


def wins_count(request):
    if request.user.is_authenticated:
        count = Listing.objects.filter(active=False, winner=request.user).count()
        return {"wins_count": count}
    return {"wins_count": 0}
