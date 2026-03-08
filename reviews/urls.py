"""
URL configuration for reviews app.
"""
from django.urls import path
from .views import ProductReviewListView, create_review, mark_helpful, user_reviews

app_name = 'reviews'

urlpatterns = [
    path('product/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),
    path('create/', create_review, name='create-review'),
    path('<int:review_id>/helpful/', mark_helpful, name='mark-helpful'),
    path('my-reviews/', user_reviews, name='user-reviews'),
]


