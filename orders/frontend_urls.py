"""
Frontend URL configuration for orders app.
"""
from django.urls import path
from .frontend_views import order_success_view

urlpatterns = [
    path('order-success/<str:order_number>/', order_success_view, name='order-success'),
]


