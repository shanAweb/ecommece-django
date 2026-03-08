"""
Admin configuration for orders app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingMethod, Coupon, CouponUsage


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_sku', 'variant_name', 'unit_price', 'total_price')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    
    list_display = ('order_number', 'user', 'status_badge', 'payment_status_badge', 
                   'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'shipped_at', 'delivered_at')
    search_fields = ('order_number', 'user__email', 'shipping_email', 'tracking_number')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Shipping Information', {
            'fields': ('shipping_full_name', 'shipping_email', 'shipping_phone',
                      'shipping_address_line1', 'shipping_address_line2',
                      'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Billing Information', {
            'fields': ('billing_full_name', 'billing_address_line1', 'billing_address_line2',
                      'billing_city', 'billing_state', 'billing_postal_code', 'billing_country')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('order_notes', 'gift_message'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'carrier')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
            'refunded': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        """Display payment status with colored badge."""
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'gray',
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment Status'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model."""
    
    list_display = ('order', 'product_name', 'variant_name', 'quantity', 'unit_price', 'total_price')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product_name', 'product_sku')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """Admin configuration for ShippingMethod model."""
    
    list_display = ('name', 'cost', 'estimated_days', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('display_order', 'cost')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin configuration for Coupon model."""
    
    list_display = ('code', 'discount_type', 'discount_value', 'uses_count', 'max_uses', 
                   'is_active', 'valid_from', 'valid_until')
    list_filter = ('is_active', 'discount_type', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('uses_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'description', 'discount_type', 'discount_value')
        }),
        ('Usage Conditions', {
            'fields': ('min_purchase_amount', 'max_uses', 'uses_count', 'max_uses_per_user')
        }),
        ('Validity Period', {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Admin configuration for CouponUsage model."""
    
    list_display = ('coupon', 'user', 'order', 'discount_amount', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('coupon__code', 'user__email', 'order__order_number')
    readonly_fields = ('used_at',)
    
    def has_add_permission(self, request):
        return False


