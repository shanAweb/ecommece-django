"""
Frontend views for cart app.
"""
from django.shortcuts import render


def cart_view(request):
    """Shopping cart page."""
    return render(request, 'cart/cart.html')


def checkout_view(request):
    """Checkout page."""
    return render(request, 'cart/checkout.html')

