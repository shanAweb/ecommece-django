"""
Frontend views for orders app.
"""
from django.shortcuts import render


def order_success_view(request, order_number: str):
    """Order success/confirmation page."""
    return render(request, 'orders/order_success.html', { 'order_number': order_number })


