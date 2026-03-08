"""
Admin configuration for cart app.
"""
from django.contrib import admin
from .models import Cart, CartItem, SavedForLater


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)
    
    def total_price(self, obj):
        return f"${obj.total_price:.2f}"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""
    
    list_display = ('user', 'total_items', 'subtotal', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model."""
    
    list_display = ('cart', 'product', 'variant', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__email', 'product__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SavedForLater)
class SavedForLaterAdmin(admin.ModelAdmin):
    """Admin configuration for SavedForLater model."""
    
    list_display = ('user', 'product', 'variant', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__name')
    readonly_fields = ('created_at',)


