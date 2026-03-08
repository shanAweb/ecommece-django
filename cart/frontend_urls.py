"""
Frontend URL configuration for cart app.
"""
from django.urls import path
from .frontend_views import cart_view, checkout_view

urlpatterns = [
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
]

