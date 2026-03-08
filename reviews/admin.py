"""
Admin configuration for reviews app.
"""
from django.contrib import admin
from .models import Review, ReviewImage, ReviewHelpful


class ReviewImageInline(admin.TabularInline):
    """Inline admin for review images."""
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 
                   'helpful_count', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')
    inlines = [ReviewImageInline]


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    """Admin configuration for ReviewHelpful model."""
    
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('review__product__name', 'user__email')


