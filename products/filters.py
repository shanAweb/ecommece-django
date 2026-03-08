"""
Filters for products app.
"""
import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter for products."""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    is_featured = django_filters.BooleanFilter()
    is_new = django_filters.BooleanFilter()
    is_on_sale = django_filters.BooleanFilter()
    stock_status = django_filters.ChoiceFilter(choices=Product.STOCK_STATUS_CHOICES)
    
    class Meta:
        model = Product
        fields = ['name', 'min_price', 'max_price', 'category', 'brand', 
                 'is_featured', 'is_new', 'is_on_sale', 'stock_status']


