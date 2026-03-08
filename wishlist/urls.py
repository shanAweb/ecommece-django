"""
URL configuration for wishlist app.
"""
from django.urls import path
from .views import WishlistListView, add_to_wishlist, remove_from_wishlist, check_in_wishlist

app_name = 'wishlist'

urlpatterns = [
    path('', WishlistListView.as_view(), name='wishlist-list'),
    path('add/<int:product_id>/', add_to_wishlist, name='add-to-wishlist'),
    path('remove/<int:product_id>/', remove_from_wishlist, name='remove-from-wishlist'),
    path('check/<int:product_id>/', check_in_wishlist, name='check-in-wishlist'),
]


