"""
Views for reviews app.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Review, ReviewHelpful
from products.models import Product
from orders.models import OrderItem
from .serializers import ReviewSerializer, CreateReviewSerializer


class ProductReviewListView(generics.ListAPIView):
    """List reviews for a product."""
    
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Get approved reviews for product."""
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(
            product_id=product_id,
            is_approved=True
        ).select_related('user').prefetch_related('images')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    """Create a product review."""
    serializer = CreateReviewSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    product = serializer.validated_data['product']
    
    # Check if user has already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        return Response({
            'error': 'You have already reviewed this product.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has purchased this product
    is_verified_purchase = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__payment_status='paid'
    ).exists()
    
    # Create review
    review = serializer.save(
        user=request.user,
        is_verified_purchase=is_verified_purchase
    )
    
    return Response({
        'message': 'Review submitted successfully.',
        'review': ReviewSerializer(review).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_helpful(request, review_id):
    """Mark review as helpful."""
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user has already voted
    vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': True}
    )
    
    if created:
        # Update helpful count
        review.helpful_count += 1
        review.save()
        
        return Response({
            'message': 'Review marked as helpful.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'You have already voted on this review.'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reviews(request):
    """Get current user's reviews."""
    reviews = Review.objects.filter(user=request.user).select_related('product')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


