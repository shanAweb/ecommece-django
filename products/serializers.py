"""
Serializers for products app.
"""
from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductAttribute, Banner


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    
    product_count = serializers.SerializerMethodField()
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'image', 
                 'full_path', 'product_count', 'is_active', 'display_order')
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brands."""
    
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'description', 'logo', 'website', 
                 'product_count', 'is_active')
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'display_order')


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants."""
    
    final_price = serializers.DecimalField(source='get_price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'name', 'size', 'color', 'price', 'final_price', 
                 'stock_quantity', 'image', 'is_active')


class ProductAttributeSerializer(serializers.ModelSerializer):
    """Serializer for product attributes."""
    
    class Meta:
        model = ProductAttribute
        fields = ('id', 'name', 'value', 'display_order')


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'sku', 'name', 'slug', 'short_description', 'category_name', 
                 'brand_name', 'price', 'compare_at_price', 'discount_percentage',
                 'primary_image', 'stock_status', 'is_featured', 'is_new', 'is_on_sale',
                 'average_rating', 'sales_count')
    
    def get_primary_image(self, obj):
        """Get primary product image."""
        try:
            primary = obj.images.filter(is_primary=True).first()
            if primary and primary.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(primary.image.url)
                return primary.image.url
            
            first_image = obj.images.first()
            if first_image and first_image.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(first_image.image.url)
                return first_image.image.url
        except Exception:
            pass
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view."""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'sku', 'name', 'slug', 'description', 'short_description',
                 'category', 'brand', 'price', 'compare_at_price', 'discount_percentage',
                 'stock_quantity', 'stock_status', 'is_low_stock', 'low_stock_threshold',
                 'weight', 'dimensions', 'material', 'meta_title', 'meta_description',
                 'is_active', 'is_featured', 'is_bestseller', 'is_new', 'is_on_sale',
                 'average_rating', 'views_count', 'sales_count', 'images', 'variants',
                 'attributes', 'created_at', 'updated_at')


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for banners."""
    
    class Meta:
        model = Banner
        fields = ('id', 'title', 'subtitle', 'description', 'image', 'mobile_image',
                 'link_url', 'button_text', 'display_order')


