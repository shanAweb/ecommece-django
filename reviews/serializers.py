"""
Serializers for reviews app.
"""
from rest_framework import serializers
from .models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for review images."""
    
    class Meta:
        model = ReviewImage
        fields = ('id', 'image')


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'user_name', 'rating', 'title', 'comment', 
                 'is_verified_purchase', 'helpful_count', 'images', 'created_at')
        read_only_fields = ('id', 'user', 'is_verified_purchase', 'helpful_count', 'created_at')


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = ('product', 'rating', 'title', 'comment')


