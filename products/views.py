"""
Views for products app.
"""
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.db import models
from django.core.cache import cache

from .models import Category, Brand, Product, Banner
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, BannerSerializer
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    """List all active categories."""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get categories with caching."""
        cache_key = 'categories_list'
        categories = cache.get(cache_key)
        
        if not categories:
            categories = list(Category.objects.filter(is_active=True))
            cache.set(cache_key, categories, 3600)  # Cache for 1 hour
        
        return categories


class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details."""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'


class BrandListView(generics.ListAPIView):
    """List all active brands."""
    
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = (AllowAny,)


class BrandDetailView(generics.RetrieveAPIView):
    """Get brand details."""
    
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'


class ProductListView(generics.ListAPIView):
    """List all active products with filtering and search."""
    
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'sales_count', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get active products with optimized queries."""
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images')
    
    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details."""
    
    serializer_class = ProductDetailSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get products with related data."""
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants', 'attributes')
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when product is viewed."""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedProductsView(generics.ListAPIView):
    """List featured products."""
    
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get featured products."""
        return Product.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BestsellerProductsView(generics.ListAPIView):
    """List bestseller products."""
    
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get bestseller products."""
        return Product.objects.filter(
            is_active=True,
            is_bestseller=True
        ).select_related('category', 'brand').prefetch_related('images').order_by('-sales_count')[:12]
    
    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class NewArrivalsView(generics.ListAPIView):
    """List new arrival products."""
    
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get new products."""
        return Product.objects.filter(
            is_active=True,
            is_new=True
        ).select_related('category', 'brand').prefetch_related('images').order_by('-created_at')[:12]
    
    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class OnSaleProductsView(generics.ListAPIView):
    """List products on sale."""
    
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get products on sale."""
        return Product.objects.filter(
            is_active=True,
            is_on_sale=True
        ).select_related('category', 'brand').prefetch_related('images')[:12]
    
    def get_serializer_context(self):
        """Add request to serializer context for image URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class RelatedProductsView(generics.ListAPIView):
    """List related products based on category."""
    
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get related products from same category."""
        slug = self.kwargs.get('slug')
        try:
            product = Product.objects.get(slug=slug, is_active=True)
            return Product.objects.filter(
                is_active=True,
                category=product.category
            ).exclude(id=product.id).select_related(
                'category', 'brand'
            ).prefetch_related('images')[:6]
        except Product.DoesNotExist:
            return Product.objects.none()


class BannerListView(generics.ListAPIView):
    """List active banners."""
    
    serializer_class = BannerSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get active banners."""
        from django.utils import timezone
        now = timezone.now()
        
        return Banner.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__lte=now) | Q(start_date__isnull=True)
        ).filter(
            Q(end_date__gte=now) | Q(end_date__isnull=True)
        ).order_by('display_order')


@api_view(['GET'])
@permission_classes([AllowAny])
def product_filters(request):
    """Get available product filters (price range, brands, categories)."""
    
    # Get active products
    products = Product.objects.filter(is_active=True)
    
    # Price range
    price_range = products.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    # Brands with product count
    brands = Brand.objects.filter(
        is_active=True,
        products__is_active=True
    ).annotate(
        product_count=Count('products')
    ).values('id', 'name', 'slug', 'product_count')
    
    # Categories with product count
    categories = Category.objects.filter(
        is_active=True,
        products__is_active=True
    ).annotate(
        product_count=Count('products')
    ).values('id', 'name', 'slug', 'product_count')
    
    return Response({
        'price_range': price_range,
        'brands': list(brands),
        'categories': list(categories),
    })

