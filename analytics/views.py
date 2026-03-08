"""
Views for analytics app - Admin dashboard statistics.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, Avg, Q, F
from django.db import models
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from products.models import Product
from users.models import User
from reviews.models import Review


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """Get overall dashboard statistics."""
    
    # Date filters
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # Orders statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    today_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    week_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__date__gte=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    month_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__date__gte=month_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Product statistics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=models.F('low_stock_threshold'),
        stock_quantity__gt=0
    ).count()
    out_of_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity=0
    ).count()
    
    # Customer statistics
    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()
    new_customers_week = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        created_at__date__gte=week_ago
    ).count()
    
    # Average order value
    avg_order_value = Order.objects.filter(
        payment_status='paid'
    ).aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    return Response({
        'orders': {
            'total': total_orders,
            'pending': pending_orders,
            'processing': processing_orders,
            'shipped': shipped_orders,
            'delivered': delivered_orders,
        },
        'revenue': {
            'total': float(total_revenue),
            'today': float(today_revenue),
            'week': float(week_revenue),
            'month': float(month_revenue),
        },
        'products': {
            'total': total_products,
            'low_stock': low_stock_products,
            'out_of_stock': out_of_stock_products,
        },
        'customers': {
            'total': total_customers,
            'new_this_week': new_customers_week,
        },
        'average_order_value': float(avg_order_value),
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_chart(request):
    """Get sales data for charts."""
    
    period = request.GET.get('period', 'week')  # week, month, year
    
    if period == 'week':
        days = 7
    elif period == 'month':
        days = 30
    else:
        days = 365
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Get daily sales
    sales_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        revenue = Order.objects.filter(
            payment_status='paid',
            created_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        orders_count = Order.objects.filter(
            payment_status='paid',
            created_at__date=date
        ).count()
        
        sales_data.append({
            'date': str(date),
            'revenue': float(revenue),
            'orders': orders_count,
        })
    
    return Response({
        'period': period,
        'data': sales_data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def top_products(request):
    """Get top selling products."""
    
    limit = int(request.GET.get('limit', 10))
    
    products = Product.objects.filter(
        is_active=True
    ).order_by('-sales_count')[:limit]
    
    data = [{
        'id': p.id,
        'name': p.name,
        'sku': p.sku,
        'sales_count': p.sales_count,
        'revenue': float(p.price * p.sales_count),
        'stock_quantity': p.stock_quantity,
    } for p in products]
    
    return Response({'products': data})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def recent_orders(request):
    """Get recent orders."""
    
    limit = int(request.GET.get('limit', 10))
    
    orders = Order.objects.select_related('user').order_by('-created_at')[:limit]
    
    data = [{
        'id': o.id,
        'order_number': o.order_number,
        'user_email': o.user.email,
        'status': o.status,
        'payment_status': o.payment_status,
        'total_amount': float(o.total_amount),
        'created_at': o.created_at,
    } for o in orders]
    
    return Response({'orders': data})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def customer_stats(request):
    """Get customer statistics."""
    
    # Top customers by order count
    top_customers = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount', filter=Q(orders__payment_status='paid'))
    ).order_by('-total_spent')[:10]
    
    data = [{
        'id': c.id,
        'email': c.email,
        'name': c.get_full_name(),
        'order_count': c.order_count,
        'total_spent': float(c.total_spent or 0),
    } for c in top_customers]
    
    return Response({'customers': data})

