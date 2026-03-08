"""
Serializers for orders app.
"""
from rest_framework import serializers
from .models import Order, OrderItem, ShippingMethod, Coupon, CouponUsage


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'product_sku', 'variant_name', 
                 'quantity', 'unit_price', 'total_price')


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'status', 'status_display', 'payment_status', 
                 'payment_status_display', 'shipping_full_name', 'shipping_email', 
                 'shipping_phone', 'shipping_address_line1', 'shipping_address_line2',
                 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
                 'billing_full_name', 'billing_address_line1', 'billing_address_line2',
                 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
                 'subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount',
                 'order_notes', 'gift_message', 'tracking_number', 'carrier',
                 'items', 'created_at', 'updated_at', 'shipped_at', 'delivered_at')
        read_only_fields = ('id', 'order_number', 'created_at', 'updated_at')


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'status', 'status_display', 'payment_status',
                 'payment_status_display', 'total_amount', 'item_count', 'created_at')
    
    def get_item_count(self, obj):
        return obj.items.count()


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order."""
    
    # Shipping information
    shipping_full_name = serializers.CharField(max_length=255)
    shipping_email = serializers.EmailField()
    shipping_phone = serializers.CharField(max_length=17)
    shipping_address_line1 = serializers.CharField(max_length=255)
    shipping_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default='United States')
    
    # Billing information
    billing_same_as_shipping = serializers.BooleanField(default=True)
    billing_full_name = serializers.CharField(max_length=255, required=False)
    billing_address_line1 = serializers.CharField(max_length=255, required=False)
    billing_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    billing_city = serializers.CharField(max_length=100, required=False)
    billing_state = serializers.CharField(max_length=100, required=False)
    billing_postal_code = serializers.CharField(max_length=20, required=False)
    billing_country = serializers.CharField(max_length=100, required=False)
    
    # Additional information
    shipping_method_id = serializers.IntegerField(required=False)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    order_notes = serializers.CharField(required=False, allow_blank=True)
    gift_message = serializers.CharField(required=False, allow_blank=True)
    
    # Payment
    payment_method = serializers.CharField(max_length=50)


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods."""
    
    class Meta:
        model = ShippingMethod
        fields = ('id', 'name', 'description', 'cost', 'estimated_days')


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons."""
    
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'description', 'discount_type', 'discount_value',
                 'min_purchase_amount', 'valid_from', 'valid_until')


class ValidateCouponSerializer(serializers.Serializer):
    """Serializer for validating coupon."""
    
    code = serializers.CharField(max_length=50)
    cart_total = serializers.DecimalField(max_digits=10, decimal_places=2)


