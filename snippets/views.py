from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Snippet
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from .permissions import premium_required
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Profile
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import DiagnosisForm
from .models import Diagnosis
from .services import judge_result_type
from django.http import FileResponse, Http404
import os
from django.views.decorators.http import require_http_methods

stripe.api_key = settings.STRIPE_SECRET_KEY
# Stripeの「Price ID」（例: price_***）を環境変数などで管理
STRIPE_PRICE_ID = getattr(settings, "STRIPE_PRICE_ID", None) or "price_xxx"

def diagnosis_start(request):
    if request.method == "POST":
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            result_type = judge_result_type(form.cleaned_data)
            user = request.user if request.user.is_authenticated else None
            d = Diagnosis.objects.create(
                user=user,
                q1_status=form.cleaned_data["q1_status"],
                q2_time=form.cleaned_data["q2_time"],
                q3_strength=form.cleaned_data["q3_strength"],
                q4_risk=form.cleaned_data["q4_risk"],
                q5_goal=form.cleaned_data["q5_goal"],
                result_type=result_type,
            )
            return redirect("diagnosis_result", pk=d.pk)
    else:
        form = DiagnosisForm()

    return render(request, "snippets/diagnosis_form.html", {"form": form})


from django.shortcuts import render, get_object_or_404

def diagnosis_result(request, pk: int):
    # ログインしていれば「自分の診断」だけ
    if request.user.is_authenticated:
        d = get_object_or_404(Diagnosis, pk=pk, user=request.user)
        is_premium = hasattr(request.user, "profile") and request.user.profile.is_premium
    else:
        # 未ログインの場合は「匿名診断(user=NULL)」だけ見せる
        d = get_object_or_404(Diagnosis, pk=pk, user__isnull=True)
        is_premium = False

    free_action = {
        "stable": "今日やる：クラウドソーシングで『自分ができる仕事』を3つ探して、案件URLをメモする。",
        "influence": "今日やる：発信テーマを1つ決めて、自己紹介ポストを下書きする（100字でOK）。",
        "attack": "今日やる：売れている商品を10個リストアップして『なぜ売れてるか』を1行で書く。",
        "build": "今日やる：解決したい悩みを1つ選び、入力→出力が1画面で完結するツール案を1つ書く。",
    }[d.result_type]

    premium_roadmap = {
        "stable": ["Day1: できる作業を棚卸し", "Day2: 提案文テンプレ作成", "Day3: 5件応募", "Day4: 初回納品の型", "Day5: 実績まとめ", "Day6: 単価UP提案", "Day7: 継続化"],
        "influence": ["Day1: テーマ決定", "Day2: 3本下書き", "Day3: 投稿", "Day4: 型を作る", "Day5: 導線整備", "Day6: 商品案", "Day7: 初販売導線"],
        "attack": ["Day1: ジャンル決定", "Day2: 仕入れ基準", "Day3: 10商品調査", "Day4: 出品", "Day5: 改善", "Day6: 回転強化", "Day7: 仕組み化"],
        "build": ["Day1: ペイン選定", "Day2: 1画面プロト", "Day3: 使う人1人", "Day4: 改善", "Day5: 課金ポイント", "Day6: LP", "Day7: 初期募集"],
    }[d.result_type]

    return render(
        request,
        "snippets/diagnosis_result.html",
        {"d": d, "is_premium": is_premium, "free_action": free_action, "premium_roadmap": premium_roadmap},
    )

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return HttpResponseBadRequest("Invalid webhook")

    event_type = event["type"]
    data_obj = event["data"]["object"]

    # サブスク開始（Checkout完了）
    if event_type == "checkout.session.completed":
        user_id = (data_obj.get("metadata") or {}).get("user_id")
        subscription_id = data_obj.get("subscription")
        customer_id = data_obj.get("customer")

        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            profile = user.profile
            profile.is_premium = True
            profile.stripe_customer_id = customer_id or profile.stripe_customer_id
            profile.stripe_subscription_id = subscription_id or profile.stripe_subscription_id
            profile.save()

    # 支払い失敗や解約でOFFにする（最低限）
    if event_type in ("customer.subscription.deleted",):
        sub_id = data_obj.get("id")
        Profile.objects.filter(stripe_subscription_id=sub_id).update(is_premium=False)

    return HttpResponse(status=200)



@login_required
@require_POST
def create_checkout_session(request):
        
    if not settings.STRIPE_SECRET_KEY:
        raise ValueError("STRIPE_SECRET_KEY is not set")
    
    # Profile を必ず用意
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Customer を必ず用意
    if not profile.stripe_customer_id:
        customer = stripe.Customer.create(email=request.user.email or None)
        profile.stripe_customer_id = customer["id"]
        profile.save(update_fields=["stripe_customer_id"])

    # 必須設定チェック（ここで落として原因を明確化）
    if not getattr(settings, "STRIPE_PRICE_ID", None):
        raise ValueError("STRIPE_PRICE_ID is not set")

    domain = settings.SITE_URL

    # ここで必ず session を作る（分岐させない）
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=profile.stripe_customer_id,
        line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        success_url=domain + "/billing/success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=domain + "/billing/cancel/",
    )

    # ここで必ず redirect
    return redirect(session.url)

@login_required
def premium_page(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return render(request, "snippets/premium_required.html")
    return render(request, "snippets/premium.html")

class SnippetListView(ListView):
    model = Snippet
    template_name = "snippets/snippet_list.html"
    context_object_name = "snippets"

class SnippetDetailView(DetailView):
    model = Snippet
    template_name = "snippets/snippet_detail.html"

class SnippetCreateView(LoginRequiredMixin, CreateView):
    model = Snippet
    fields = ["title", "code"]
    template_name = "snippets/snippet_form.html"
    success_url = reverse_lazy("snippet_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
        
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.created_by == self.request.user
        
class SnippetUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Snippet
    fields = ["title", "code"]
    template_name = "snippets/snippet_form.html"
    success_url = reverse_lazy("snippet_list")

class SnippetDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Snippet
    template_name = "snippets/snippet_confirm_delete.html"
    success_url = reverse_lazy("snippet_list")

from django.shortcuts import render, redirect
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Profile


@login_required
def billing_success(request):
    session_id = request.GET.get("session_id")

    # 直アクセスでも、すでにPremiumなら成功ページを見せる
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not session_id:
        if profile.is_premium:
            return render(request, "snippets/billing_success.html")
        return redirect("billing_cancel")

    # session_id があるときだけ Stripeから情報を取りに行ってPremium確定
    session = stripe.checkout.Session.retrieve(session_id)
    profile.stripe_customer_id = session.get("customer")
    profile.stripe_subscription_id = session.get("subscription")
    profile.is_premium = True
    profile.save(update_fields=["stripe_customer_id", "stripe_subscription_id", "is_premium"])

    return render(request, "snippets/billing_success.html")

def billing_cancel(request):
    return render(request, "snippets/billing_cancel.html")

from django.shortcuts import redirect
from pathlib import Path

@login_required
def premium_download_stable(request):
    # Premiumチェック
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return redirect("premium_page")

    # PDFの実体パス（あなたの配置：プロジェクト直下 static/premium/）
    pdf_path = Path(settings.BASE_DIR) / "static" / "premium" / "stable_7day_roadmap.pdf"
    if not pdf_path.exists():
        raise Http404(f"PDF not found: {pdf_path}")

    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename="stable_7day_roadmap.pdf",
        content_type="application/pdf",
    )

