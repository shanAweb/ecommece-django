"""
Views for search app.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q

from products.models import Product
from products.serializers import ProductListSerializer
from .models import SearchQuery


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """Search products."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'results': [],
            'count': 0
        })
    
    # Search in product name, description, SKU
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(sku__icontains=query) |
        Q(category__name__icontains=query) |
        Q(brand__name__icontains=query),
        is_active=True
    ).select_related('category', 'brand').prefetch_related('images').distinct()
    
    # Track search query
    SearchQuery.objects.create(
        query=query,
        results_count=products.count()
    )
    
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'query': query,
        'results': serializer.data,
        'count': products.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """Get search suggestions/autocomplete."""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response({'suggestions': []})
    
    # Get product suggestions
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('id', 'name', 'slug')[:10]
    
    return Response({
        'suggestions': list(products)
    })


