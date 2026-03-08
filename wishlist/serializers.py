"""
Serializers for wishlist app.
"""
from rest_framework import serializers
from .models import Wishlist
from products.serializers import ProductListSerializer


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist."""
    
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ('id', 'product', 'created_at')
        read_only_fields = ('id', 'created_at')


