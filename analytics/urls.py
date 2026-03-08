"""
URL configuration for analytics app.
"""
from django.urls import path
from .views import dashboard_stats, sales_chart, top_products, recent_orders, customer_stats

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', dashboard_stats, name='dashboard-stats'),
    path('sales-chart/', sales_chart, name='sales-chart'),
    path('top-products/', top_products, name='top-products'),
    path('recent-orders/', recent_orders, name='recent-orders'),
    path('customer-stats/', customer_stats, name='customer-stats'),
]


