"""
URL configuration for products API.
"""
from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, BrandListView, BrandDetailView,
    ProductListView, ProductDetailView, FeaturedProductsView, BestsellerProductsView,
    NewArrivalsView, OnSaleProductsView, RelatedProductsView, BannerListView,
    product_filters
)

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Brands
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/<slug:slug>/', BrandDetailView.as_view(), name='brand-detail'),
    
    # Products
    path('', ProductListView.as_view(), name='product-list'),
    path('featured/', FeaturedProductsView.as_view(), name='featured-products'),
    path('bestsellers/', BestsellerProductsView.as_view(), name='bestseller-products'),
    path('new-arrivals/', NewArrivalsView.as_view(), name='new-arrivals'),
    path('on-sale/', OnSaleProductsView.as_view(), name='on-sale'),
    path('filters/', product_filters, name='product-filters'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/related/', RelatedProductsView.as_view(), name='related-products'),
    
    # Banners
    path('banners/list/', BannerListView.as_view(), name='banner-list'),
]


