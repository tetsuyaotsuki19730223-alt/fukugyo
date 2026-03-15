from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import redirect


stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):

    session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=[

            {
                "price": "price_1TB9dLBsXWS49O2C4EqLauw5",
                "quantity": 1,
            }

        ],

        mode="subscription",

        success_url="http://localhost:8000/dashboard/",

        cancel_url="http://localhost:8000/pricing/",
    )

    return redirect(session.url)


def pricing(request):
    return render(request, "snippets/pricing.html")


def create_checkout(request):
    return render(request, "snippets/checkout.html")


def premium_page(request):
    return render(request, "snippets/premium.html")
