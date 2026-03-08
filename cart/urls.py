"""
URL configuration for cart app.
"""
from django.urls import path
from .views import (
    get_cart, add_to_cart, update_cart_item, remove_cart_item, clear_cart,
    get_saved_items, save_for_later, move_to_cart, remove_saved_item
)

app_name = 'cart'

urlpatterns = [
    # Cart
    path('', get_cart, name='get-cart'),
    path('add/', add_to_cart, name='add-to-cart'),
    path('items/<int:item_id>/update/', update_cart_item, name='update-cart-item'),
    path('items/<int:item_id>/remove/', remove_cart_item, name='remove-cart-item'),
    path('clear/', clear_cart, name='clear-cart'),
    
    # Saved for later
    path('saved/', get_saved_items, name='get-saved-items'),
    path('items/<int:item_id>/save/', save_for_later, name='save-for-later'),
    path('saved/<int:item_id>/move/', move_to_cart, name='move-to-cart'),
    path('saved/<int:item_id>/remove/', remove_saved_item, name='remove-saved-item'),
]


