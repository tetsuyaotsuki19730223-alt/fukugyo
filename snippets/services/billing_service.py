import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout(user):

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        client_reference_id=user.id,
        line_items=[{
            "price": settings.STRIPE_PRICE_ID,
            "quantity": 1
        }]
    )

    return session