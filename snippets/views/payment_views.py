from django.shortcuts import render, redirect
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY or ""



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

        success_url="https://ai-sidejob-coach.net/dashboard/",

        cancel_url="https://ai-sidejob-coach.net/pricing/",
    )

    return redirect(session.url)

def pricing(request):
    return render(request, "snippets/pricing.html")


def create_checkout(request):
    return render(request, "snippets/checkout.html")


def premium_page(request):
    return render(request, "snippets/premium.html")
