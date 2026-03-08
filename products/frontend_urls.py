"""
Frontend URL configuration for products app.
"""
from django.urls import path
from .frontend_views import (
    index, product_list, product_detail, category_list,
    terms_view, privacy_view, returns_view, contact_view
)

urlpatterns = [
    path('', index, name='index'),
    path('products/', product_list, name='product-list'),
    path('products/<slug:slug>/', product_detail, name='product-detail'),
    path('categories/', category_list, name='category-list'),
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    path('returns/', returns_view, name='returns'),
    path('contact/', contact_view, name='contact'),
]


