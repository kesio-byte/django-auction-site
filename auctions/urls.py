from django.urls import path

from . import views

# ---- auctions/urls.py ----
# Defines URL patterns for the auctions app, mapping routes to view functions
urlpatterns = [
    path("my_listings", views.my_listings, name="my_listings"),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing_detail, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_listings, name="category_listings"),
    path("closed_listings", views.closed_listings, name="closed_listings"),
    path("my-wins/", views.my_wins, name="my_wins"),

]
