from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Category
from .forms import CreateListingForm, ListingForm
from .forms import BidForm
from django.utils import timezone
from .models import Listing

from .forms import CommentForm

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all()
    highest_bid = listing.bids.order_by("-amount").first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # --- Handle Comment ---
        if form_type == "comment" and request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.listing = listing
                comment.commenter = request.user
                comment.save()
                messages.success(request, "Comment added.")
                return redirect("listing", listing_id=listing.id)
            else:
                messages.error(request, "Invalid comment.")
            bid_form = BidForm()  # keep bid form fresh

        # --- Handle Bid ---
        elif form_type == "bid" and request.user.is_authenticated:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                amount = bid_form.cleaned_data["bid"]
                if amount > float(current_price):
                    Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
                    messages.success(request, "Bid placed successfully!")
                else:
                    messages.error(request, "Bid must be greater than current price.")
                return redirect("listing", listing_id=listing.id)
            else:
                messages.error(request, "Invalid bid.")
            comment_form = CommentForm()

        # --- Handle Watchlist ---
        elif form_type == "watchlist" and request.user.is_authenticated:
            if listing in request.user.watchlist.all():
                request.user.watchlist.remove(listing)
                messages.info(request, "Removed from watchlist.")
            else:
                request.user.watchlist.add(listing)
                messages.success(request, "Added to watchlist.")
            return redirect("listing", listing_id=listing.id)
            # keep forms fresh
            comment_form = CommentForm()
            bid_form = BidForm()

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
            comment_form = CommentForm()
            bid_form = BidForm()

        else:
            # default forms if POST type not recognized
            comment_form = CommentForm()
            bid_form = BidForm()

    else:
        comment_form = CommentForm()
        bid_form = BidForm()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "current_price": current_price,
        "highest_bid": highest_bid,
        "comment_form": comment_form,
        "form": bid_form
    })


def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Determine current price using property
    highest_bid = listing.bids.order_by("-amount").first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid
    
    # Handle POST actions
    if request.method == "POST":
        # --- Place Bid ---
        if "bid" in request.POST and request.user.is_authenticated:
            if not listing.active:
                messages.error(request, "This auction is closed. No more bids allowed.")
                return redirect("listing", listing_id=listing.id)

            form = BidForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["bid"]
                if amount > float(current_price):
                    Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
                    messages.success(request, "Bid placed successfully!")
                else:
                    messages.error(request, "Bid must be greater than current price.")
            else:
                messages.error(request, "Invalid bid. Please enter a number.")
            return redirect("listing", listing_id=listing.id)

        # --- Add Comment ---
        elif "comment" in request.POST and request.user.is_authenticated:
            if not listing.active:
                messages.error(request, "This auction is closed. No more comments allowed.")
                return redirect("listing", listing_id=listing.id)

            text = request.POST["comment"]
            Comment.objects.create(listing=listing, commenter=request.user, text=text)
            messages.success(request, "Comment added.")
            return redirect("listing", listing_id=listing.id)

        # --- Toggle Watchlist ---
        elif "watchlist" in request.POST and request.user.is_authenticated:
            if listing in request.user.watchlist.all():
                request.user.watchlist.remove(listing)
                messages.info(request, "Removed from watchlist.")
            else:
                request.user.watchlist.add(listing)
                messages.success(request, "Added to watchlist.")
            return redirect("listing", listing_id=listing.id)

        # --- Close Auction ---
        elif "close" in request.POST and request.user == listing.owner:
            listing.active = False
            listing.closed_at = timezone.now()  # record closure time
            highest_bid = listing.bids.order_by("-amount").first()
            if highest_bid:
                listing.winner = highest_bid.bidder
                listing.final_price = highest_bid.amount  # save final price
                messages.info(request, f"Auction closed. Winner: {highest_bid.bidder.username}")
            else:
                listing.final_price = listing.starting_bid  # fallback if no bids
                messages.info(request, "Auction closed. No bids were placed.")
            listing.save()
            return redirect("listing", listing_id=listing.id)

    # Render detail page
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_price": current_price,
        "highest_bid": highest_bid,
        "comments": listing.comments.all(),
        "form": BidForm()
    })
def categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.active_count = category.listings.filter(active=True).count()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listings(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(active=True, category=category)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST, request.FILES)  # include request.FILES
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
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user)
    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })


@login_required
def closed_listings(request):
    listings = Listing.objects.filter(active=False)
    return render(request, "auctions/closed_listings.html", {
        "listings": listings
    })

@login_required
def my_wins(request):
    # Get all closed listings where the current user is the winner
    listings = Listing.objects.filter(active=False, winner=request.user)
    return render(request, "auctions/my_wins.html", {
        "listings": listings
    })

def wins_count(request):
    if request.user.is_authenticated:
        count = Listing.objects.filter(active=False, winner=request.user).count()
        return {"wins_count": count}
    return {"wins_count": 0}

