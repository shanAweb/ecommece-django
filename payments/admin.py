"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = ('id', 'order', 'user', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin configuration for Refund model."""
    
    list_display = ('id', 'order', 'amount', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('order__order_number', 'description')
    readonly_fields = ('created_at', 'processed_at')


