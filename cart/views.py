"""
Views for cart app.
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, SavedForLater
from products.models import Product, ProductVariant
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, SavedForLaterSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """Get user's cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add item to cart."""
    serializer = AddToCartSerializer(data=request.data)
    
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Get product
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Get variant if specified
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        
        # Check stock
        available_stock = variant.stock_quantity if variant else product.stock_quantity
        if quantity > available_stock:
            return Response({
                'error': f'Only {available_stock} items available in stock.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if new_quantity > available_stock:
                return Response({
                    'error': f'Cannot add more. Only {available_stock} items available.'
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            'message': 'Item added to cart successfully.',
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    serializer = UpdateCartItemSerializer(data=request.data)
    
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity == 0:
            # Remove item if quantity is 0
            cart_item.delete()
            message = 'Item removed from cart.'
        else:
            # Check stock
            available_stock = cart_item.variant.stock_quantity if cart_item.variant else cart_item.product.stock_quantity
            if quantity > available_stock:
                return Response({
                    'error': f'Only {available_stock} items available in stock.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Cart item updated successfully.'
        
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            'message': message,
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    """Remove item from cart."""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    
    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response({
        'message': 'Item removed from cart.',
        'cart': cart_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from cart."""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    
    return Response({
        'message': 'Cart cleared successfully.'
    }, status=status.HTTP_200_OK)


# Saved for later views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_items(request):
    """Get saved for later items."""
    saved_items = SavedForLater.objects.filter(user=request.user).select_related('product')
    serializer = SavedForLaterSerializer(saved_items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_for_later(request, item_id):
    """Move cart item to saved for later."""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    # Create saved item
    SavedForLater.objects.get_or_create(
        user=request.user,
        product=cart_item.product,
        variant=cart_item.variant
    )
    
    # Remove from cart
    cart_item.delete()
    
    return Response({
        'message': 'Item saved for later.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_to_cart(request, item_id):
    """Move saved item back to cart."""
    saved_item = get_object_or_404(SavedForLater, id=item_id, user=request.user)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add to cart
    CartItem.objects.get_or_create(
        cart=cart,
        product=saved_item.product,
        variant=saved_item.variant,
        defaults={'quantity': 1}
    )
    
    # Remove from saved
    saved_item.delete()
    
    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response({
        'message': 'Item moved to cart.',
        'cart': cart_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_saved_item(request, item_id):
    """Remove saved for later item."""
    saved_item = get_object_or_404(SavedForLater, id=item_id, user=request.user)
    saved_item.delete()
    
    return Response({
        'message': 'Saved item removed.'
    }, status=status.HTTP_200_OK)


