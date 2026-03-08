"""
URL configuration for payments app.
"""
from django.urls import path
from .views import create_payment_intent, confirm_payment, stripe_webhook

app_name = 'payments'

urlpatterns = [
    path('<str:order_number>/create-intent/', create_payment_intent, name='create-payment-intent'),
    path('<str:order_number>/confirm/', confirm_payment, name='confirm-payment'),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]


