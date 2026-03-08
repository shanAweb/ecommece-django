"""
Views for orders app.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import Order, OrderItem, ShippingMethod, Coupon, CouponUsage
from .serializers import (
    OrderSerializer, OrderListSerializer, CreateOrderSerializer,
    ShippingMethodSerializer, ValidateCouponSerializer
)
from cart.models import Cart


class OrderListView(generics.ListAPIView):
    """List user's orders."""
    
    serializer_class = OrderListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Get orders for current user."""
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details."""
    
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders for current user."""
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create order from cart."""
    serializer = CreateOrderSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get cart
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not cart.items.exists():
        return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Shipping optional: default to 0 if not provided
    shipping_cost = 0
    shipping_method = None
    shipping_method_id = serializer.validated_data.get('shipping_method_id')
    if shipping_method_id:
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            shipping_cost = shipping_method.cost
        except ShippingMethod.DoesNotExist:
            return Response({'error': 'Invalid shipping method.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate totals
    subtotal = cart.subtotal
    tax_amount = 0  # Calculate tax based on your requirements
    discount_amount = 0
    
    # Validate and apply coupon if provided
    coupon = None
    coupon_code = serializer.validated_data.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper())
            is_valid, message = coupon.is_valid()
            
            if not is_valid:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user has already used this coupon
            usage_count = CouponUsage.objects.filter(
                coupon=coupon,
                user=request.user
            ).count()
            
            if usage_count >= coupon.max_uses_per_user:
                return Response({
                    'error': 'You have already used this coupon the maximum number of times.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check minimum purchase amount
            if subtotal < coupon.min_purchase_amount:
                return Response({
                    'error': f'Minimum purchase amount of ${coupon.min_purchase_amount} required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate discount
            discount_amount = coupon.calculate_discount(subtotal)
            
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code.'}, status=status.HTTP_400_BAD_REQUEST)
    
    total_amount = subtotal + shipping_cost + tax_amount - discount_amount
    
    # Prepare billing information
    billing_data = {}
    if serializer.validated_data.get('billing_same_as_shipping', True):
        billing_data = {
            'billing_full_name': serializer.validated_data['shipping_full_name'],
            'billing_address_line1': serializer.validated_data['shipping_address_line1'],
            'billing_address_line2': serializer.validated_data.get('shipping_address_line2', ''),
            'billing_city': serializer.validated_data['shipping_city'],
            'billing_state': serializer.validated_data['shipping_state'],
            'billing_postal_code': serializer.validated_data['shipping_postal_code'],
            'billing_country': serializer.validated_data['shipping_country'],
        }
    else:
        billing_data = {
            'billing_full_name': serializer.validated_data['billing_full_name'],
            'billing_address_line1': serializer.validated_data['billing_address_line1'],
            'billing_address_line2': serializer.validated_data.get('billing_address_line2', ''),
            'billing_city': serializer.validated_data['billing_city'],
            'billing_state': serializer.validated_data['billing_state'],
            'billing_postal_code': serializer.validated_data['billing_postal_code'],
            'billing_country': serializer.validated_data['billing_country'],
        }
    
    # Create order with transaction
    with transaction.atomic():
        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_full_name=serializer.validated_data['shipping_full_name'],
            shipping_email=serializer.validated_data['shipping_email'],
            shipping_phone=serializer.validated_data['shipping_phone'],
            shipping_address_line1=serializer.validated_data['shipping_address_line1'],
            shipping_address_line2=serializer.validated_data.get('shipping_address_line2', ''),
            shipping_city=serializer.validated_data['shipping_city'],
            shipping_state=serializer.validated_data['shipping_state'],
            shipping_postal_code=serializer.validated_data['shipping_postal_code'],
            shipping_country=serializer.validated_data['shipping_country'],
            **billing_data,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            order_notes=serializer.validated_data.get('order_notes', ''),
            gift_message=serializer.validated_data.get('gift_message', ''),
        )
        
        # Create order items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.variant.sku if cart_item.variant else cart_item.product.sku,
                variant_name=cart_item.variant.name if cart_item.variant else '',
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
            )
            
            # Update product stock
            if cart_item.variant:
                cart_item.variant.stock_quantity -= cart_item.quantity
                cart_item.variant.save()
            else:
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            
            # Update product sales count
            cart_item.product.sales_count += cart_item.quantity
            cart_item.product.save()
        
        # Record coupon usage
        if coupon:
            CouponUsage.objects.create(
                coupon=coupon,
                user=request.user,
                order=order,
                discount_amount=discount_amount
            )
            coupon.uses_count += 1
            coupon.save()
        
        # Clear cart
        cart.items.all().delete()
    
    # Return order details
    order_serializer = OrderSerializer(order)
    return Response({
        'message': 'Order created successfully.',
        'order': order_serializer.data
    }, status=status.HTTP_201_CREATED)


class ShippingMethodListView(generics.ListAPIView):
    """List available shipping methods."""
    
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = (AllowAny,)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_coupon(request):
    """Validate coupon code."""
    serializer = ValidateCouponSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    code = serializer.validated_data['code'].upper()
    cart_total = serializer.validated_data['cart_total']
    
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return Response({'error': 'Invalid coupon code.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate coupon
    is_valid, message = coupon.is_valid()
    if not is_valid:
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check user usage
    usage_count = CouponUsage.objects.filter(
        coupon=coupon,
        user=request.user
    ).count()
    
    if usage_count >= coupon.max_uses_per_user:
        return Response({
            'error': 'You have already used this coupon the maximum number of times.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check minimum purchase
    if cart_total < coupon.min_purchase_amount:
        return Response({
            'error': f'Minimum purchase amount of ${coupon.min_purchase_amount} required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    return Response({
        'message': 'Coupon is valid.',
        'coupon': {
            'code': coupon.code,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_number):
    """Cancel an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Only allow cancellation if order is pending or processing
    if order.status not in ['pending', 'processing']:
        return Response({
            'error': 'Order cannot be cancelled at this stage.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update order status
    order.status = 'cancelled'
    order.save()
    
    # Restore product stock
    with transaction.atomic():
        for item in order.items.all():
            if item.variant:
                item.variant.stock_quantity += item.quantity
                item.variant.save()
            else:
                item.product.stock_quantity += item.quantity
                item.product.save()
            
            # Update product sales count
            item.product.sales_count -= item.quantity
            item.product.save()
    
    return Response({
        'message': 'Order cancelled successfully.'
    }, status=status.HTTP_200_OK)


