from .models import Listing

def navbar_counts(request):
    if request.user.is_authenticated:
        return {
            "active_count": Listing.objects.filter(active=True).count(),
            "closed_count": Listing.objects.filter(active=False).count(),
            "my_listings_count": Listing.objects.filter(owner=request.user).count(),
            "watchlist_count": request.user.watchlist.count(),
            "wins_count": Listing.objects.filter(active=False, winner=request.user).count(),
        }
    return {
        "active_count": 0,
        "closed_count": 0,
        "my_listings_count": 0,
        "watchlist_count": 0,
        "wins_count": 0,
    }
