"""
Views for wishlist app.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Wishlist
from products.models import Product
from .serializers import WishlistSerializer


class WishlistListView(generics.ListAPIView):
    """List user's wishlist items."""
    
    serializer_class = WishlistSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Get wishlist items for current user."""
        return Wishlist.objects.filter(user=self.request.user).select_related('product')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        return Response({
            'message': 'Product added to wishlist.',
            'wishlist': WishlistSerializer(wishlist_item, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Product is already in your wishlist.'
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        product_id=product_id
    )
    wishlist_item.delete()
    
    return Response({
        'message': 'Product removed from wishlist.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_in_wishlist(request, product_id):
    """Check if product is in wishlist."""
    in_wishlist = Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).exists()
    
    return Response({
        'in_wishlist': in_wishlist
    }, status=status.HTTP_200_OK)


