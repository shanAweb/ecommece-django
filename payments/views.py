"""
Views for payments app - Stripe integration.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
import stripe

from orders.models import Order
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request, order_number):
    """Create Stripe payment intent for order."""
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Check if order is already paid
    if order.payment_status == 'paid':
        return Response({
            'error': 'Order is already paid.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'order_number': order.order_number,
                'user_email': request.user.email,
            }
        )
        
        # Create payment record
        Payment.objects.create(
            order=order,
            user=request.user,
            payment_method='stripe',
            amount=order.total_amount,
            payment_intent_id=intent.id,
            status='pending',
        )
        
        return Response({
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLIC_KEY,
        }, status=status.HTTP_200_OK)
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request, order_number):
    """Confirm payment completion."""
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment_intent_id = request.data.get('payment_intent_id')
    
    if not payment_intent_id:
        return Response({
            'error': 'Payment intent ID is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Update payment record
            payment = Payment.objects.filter(
                order=order,
                payment_intent_id=payment_intent_id
            ).first()
            
            if payment:
                payment.status = 'completed'
                payment.transaction_id = intent.id
                payment.completed_at = timezone.now()
                
                # Extract card details if available
                if intent.charges.data:
                    charge = intent.charges.data[0]
                    if charge.payment_method_details.card:
                        payment.card_last4 = charge.payment_method_details.card.last4
                        payment.card_brand = charge.payment_method_details.card.brand
                
                payment.save()
                
                # Update order status
                order.payment_status = 'paid'
                order.status = 'processing'
                order.save()
                
                return Response({
                    'message': 'Payment confirmed successfully.',
                    'order': {
                        'order_number': order.order_number,
                        'status': order.status,
                        'payment_status': order.payment_status,
                    }
                }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Payment not successful.'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # Handle different event types
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        # Handle successful payment
        pass
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        # Handle failed payment
        pass
    
    return Response(status=status.HTTP_200_OK)


