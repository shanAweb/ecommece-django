"""
URL configuration for search app.
"""
from django.urls import path
from .views import search_products, search_suggestions

app_name = 'search'

urlpatterns = [
    path('', search_products, name='search-products'),
    path('suggestions/', search_suggestions, name='search-suggestions'),
]


