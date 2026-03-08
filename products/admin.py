"""
Admin configuration for products app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductAttribute, Banner


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'display_order')


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""
    model = ProductVariant
    extra = 1
    fields = ('name', 'sku', 'size', 'color', 'price', 'stock_quantity', 'is_active')


class ProductAttributeInline(admin.TabularInline):
    """Inline admin for product attributes."""
    model = ProductAttribute
    extra = 1
    fields = ('name', 'value', 'display_order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ('name', 'parent', 'display_order', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    
    list_display = ('name', 'website', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 
                   'stock_status_badge', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'is_bestseller', 'is_new', 'is_on_sale', 
                  'stock_status', 'category', 'brand', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('sku', 'views_count', 'sales_count', 'created_at', 'updated_at')
    inlines = [ProductImageInline, ProductVariantInline, ProductAttributeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_at_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'stock_status', 'low_stock_threshold')
        }),
        ('Specifications', {
            'fields': ('weight', 'dimensions', 'material')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_bestseller', 'is_new', 'is_on_sale')
        }),
        ('Analytics', {
            'fields': ('views_count', 'sales_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status_badge(self, obj):
        """Display stock status with colored badge."""
        colors = {
            'in_stock': 'green',
            'out_of_stock': 'red',
            'pre_order': 'orange',
            'discontinued': 'gray',
        }
        color = colors.get(obj.stock_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_stock_status_display()
        )
    stock_status_badge.short_description = 'Stock Status'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""
    
    list_display = ('product', 'image_preview', 'is_primary', 'display_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    ordering = ('product', 'display_order')
    
    def image_preview(self, obj):
        """Display image thumbnail."""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for ProductVariant model."""
    
    list_display = ('product', 'name', 'sku', 'size', 'color', 'price', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'size', 'color', 'created_at')
    search_fields = ('product__name', 'sku', 'name')
    ordering = ('product', 'name')


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """Admin configuration for ProductAttribute model."""
    
    list_display = ('product', 'name', 'value', 'display_order')
    search_fields = ('product__name', 'name', 'value')
    ordering = ('product', 'display_order', 'name')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Admin configuration for Banner model."""
    
    list_display = ('title', 'is_active', 'display_order', 'start_date', 'end_date', 'created_at')
    list_filter = ('is_active', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle', 'description')
    ordering = ('display_order', '-created_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description', 'button_text', 'link_url')
        }),
        ('Images', {
            'fields': ('image', 'mobile_image')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order', 'start_date', 'end_date')
        }),
    )


