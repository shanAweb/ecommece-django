"""
Frontend URL configuration for users app.
"""
from django.urls import path
from .frontend_views import (
    register_view, login_view, dashboard_view, orders_view,
    edit_profile_view, settings_view, addresses_view, wishlist_view,
    verify_email_view
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('account/', dashboard_view, name='dashboard'),
    path('account/edit/', edit_profile_view, name='edit-profile'),
    path('account/settings/', settings_view, name='settings'),
    path('account/addresses/', addresses_view, name='addresses'),
    path('account/change-password/', settings_view, name='change-password'),  # Same as settings
    path('orders/', orders_view, name='orders'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('verify-email/<uuid:token>/', verify_email_view, name='verify-email-ui'),
]

