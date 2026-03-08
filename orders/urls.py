"""
URL configuration for orders app.
"""
from django.urls import path
from .views import (
    OrderListView, OrderDetailView, create_order, ShippingMethodListView,
    validate_coupon, cancel_order
)

app_name = 'orders'

urlpatterns = [
    # Orders
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', create_order, name='create-order'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', cancel_order, name='cancel-order'),
    
    # Shipping
    path('shipping/methods/', ShippingMethodListView.as_view(), name='shipping-methods'),
    
    # Coupons
    path('coupons/validate/', validate_coupon, name='validate-coupon'),
]


