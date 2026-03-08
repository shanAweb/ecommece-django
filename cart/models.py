"""
Models for shopping cart.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product, ProductVariant


class Cart(models.Model):
    """Shopping cart model."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
    
    def __str__(self):
        return f"Cart - {self.user.email}"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        """Calculate cart total (subtotal + shipping - discounts)."""
        # For now, just return subtotal. Can add shipping and discounts later
        return self.subtotal


class CartItem(models.Model):
    """Cart item model."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product', 'variant')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def unit_price(self):
        """Get unit price (variant price or product price)."""
        if self.variant:
            return self.variant.get_price()
        return self.product.price
    
    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.unit_price * self.quantity


class SavedForLater(models.Model):
    """Saved for later items."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_for_later'
        verbose_name = 'Saved For Later'
        verbose_name_plural = 'Saved For Later'
        unique_together = ('user', 'product', 'variant')
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


