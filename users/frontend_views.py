"""
Frontend views for users app.
"""
from django.shortcuts import render, redirect
from django.http import HttpResponse
from users.models import User
from django.contrib.auth import login
from django.contrib import messages


def register_view(request):
    """User registration page."""
    return render(request, 'users/register.html')


def login_view(request):
    """User login page."""
    return render(request, 'users/login.html')


def dashboard_view(request):
    """User dashboard/profile page."""
    return render(request, 'users/dashboard.html')


def orders_view(request):
    """User orders page."""
    return render(request, 'users/orders.html')


def edit_profile_view(request):
    """Edit profile page."""
    return render(request, 'users/edit_profile.html')


def settings_view(request):
    """Settings page with change password."""
    return render(request, 'users/settings.html')


def addresses_view(request):
    """Addresses management page."""
    return render(request, 'users/addresses.html')


def wishlist_view(request):
    """Wishlist page."""
    return render(request, 'users/wishlist.html')


def verify_email_view(request, token):
    """Pretty email verification page matching site UI.
    Marks user verified and renders success/failure state.
    """
    context = { 'success': False, 'message': 'Invalid or expired verification link.' }
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
        context['success'] = True
        context['message'] = 'Your email has been verified successfully.'
    except User.DoesNotExist:
        pass
    return render(request, 'users/verify_email.html', context)
