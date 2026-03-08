"""
Frontend views for products app.
"""
from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand


def index(request):
    """Homepage view."""
    return render(request, 'index.html')


def product_list(request):
    """Product listing page."""
    return render(request, 'products/product_list.html')


def product_detail(request, slug):
    """Product detail page."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/product_detail.html', {
        'product': product
    })


def category_list(request):
    """Category listing page."""
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    return render(request, 'products/category_list.html', {
        'categories': categories
    })


def brand_list(request):
    """Brand listing page."""
    brands = Brand.objects.filter(is_active=True).prefetch_related('products')
    return render(request, 'products/brand_list.html', {
        'brands': brands
    })


def terms_view(request):
    """Terms & Conditions page."""
    return render(request, 'legal/terms.html')


def privacy_view(request):
    """Privacy Policy page."""
    return render(request, 'legal/privacy.html')


def returns_view(request):
    """Returns page."""
    return render(request, 'legal/returns.html')


def contact_view(request):
    """Contact page."""
    return render(request, 'legal/contact.html')


