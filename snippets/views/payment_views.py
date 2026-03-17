from django.shortcuts import render, redirect
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
import uuid

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

        success_url="https://www.ai-sidejob-coach.net/success/",

        cancel_url="https://www.ai-sidejob-coach.net/pricing/",
    )

    return redirect(session.url)

def pricing(request):
    return render(request, "snippets/pricing.html")


@login_required
def create_checkout(request):

    profile = request.user.profile

    # トークン生成
    token = str(uuid.uuid4())
    profile.payment_token = token
    profile.save()

    # Lemon SqueezyのURL
    checkout_url = f"https://your-store.lemonsqueezy.com/checkout/buy/xxxx?token={token}"

    return redirect(checkout_url)

def premium_page(request):
    return render(request, "snippets/premium.html")

@login_required
def success(request):

    profile = request.user.profile
    profile.is_premium = True
    profile.save()

    return redirect("dashboard")