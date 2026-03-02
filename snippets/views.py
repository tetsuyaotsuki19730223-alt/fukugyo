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
    d = get_object_or_404(Diagnosis, pk=pk, user=request.user)
    is_premium = hasattr(request.user, "profile") and request.user.profile.is_premium

    free_action = {
        "stable": "今日やる：クラウドソーシングで『自分ができる仕事』を3つ探して、案件URLをメモする。",
        "influence": "今日やる：発信テーマを1つ決めて、自己紹介ポストを下書きする（100字でOK）。",
        "attack": "今日やる：売れている商品を10個リストアップして『なぜ売れてるか』を1行で書く。",
        "build": "今日やる：解決したい悩みを1つ選び、入力→出力が1画面で完結するツール案を1つ書く。",
    }[d.result_type]

    return render(request, "snippets/diagnosis_result.html", {
        "d": d,
        "is_premium": is_premium,
        "free_action": free_action,
    })

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

from django.conf import settings
from django.http import FileResponse
import os

@login_required
def premium_page(request):
    if not request.user.profile.is_premium:
        return render(request, "snippets/premium_required.html")

    # 最新の診断結果を取得
    d = Diagnosis.objects.filter(user=request.user).order_by("-id").first()
    if not d:
        return redirect("diagnosis_start")

    file_map = {
        "stable": "stable_7day_roadmap.pdf",
        "influence": "influence_7day_roadmap.pdf",
        "attack": "attack_7day_roadmap.pdf",
        "build": "build_7day_roadmap.pdf",
    }

    filename = file_map.get(d.result_type)
    file_path = os.path.join(settings.BASE_DIR, "static", "premium", filename)

    return FileResponse(open(file_path, "rb"), as_attachment=True)

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

    profile, _ = Profile.objects.get_or_create(user=request.user)

    # 直アクセス（session_idなし）でも、すでにPremiumなら成功ページを表示
    if not session_id:
        if profile.is_premium:
            return render(request, "snippets/billing_success.html")
        return redirect("billing_cancel")

    # session_idあり：Stripeで検証してPremium確定
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

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse
from django.shortcuts import redirect

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Profile, Diagnosis


def _register_japanese_font():
    # 例: snippets/static/fonts/ipaexg.ttf
    font_path = Path(settings.BASE_DIR) / "snippets" / "static" / "fonts" / "ipaexg.ttf"
    if not font_path.exists():
        raise FileNotFoundError(f"Japanese font not found: {font_path}")
    # フォント名は任意（ここでは IPAexGothic）
    pdfmetrics.registerFont(TTFont("IPAexGothic", str(font_path)))


def _build_roadmap_pdf(display_name: str, result_type: str) -> bytes:
    """
    名前 + タイプ別のPDFをメモリ上で生成して bytes を返す
    """
    _register_japanese_font()

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    c.setFont("IPAexGothic", 18)
    c.drawString(40, height - 60, f"{display_name} さん専用")
    c.setFont("IPAexGothic", 22)

    type_title = {
        "stable": "安定型（クラウドソーシング）",
        "influence": "影響力型（発信）",
        "attack": "攻撃型（物販/マーケ）",
        "build": "構築型（SaaS/ツール）",
    }.get(result_type, "タイプ不明")

    c.drawString(40, height - 95, f"7日ロードマップ：{type_title}")

    c.setFont("IPAexGothic", 12)
    c.drawString(40, height - 125, "※ まずは Day1 だけやればOK。タイマー15分で十分です。")

    # --- 本文（仮の中身。あとで自由に差し替えOK） ---
    roadmap = {
        "stable": [
            "Day1: 案件を3つ探してURLをメモ",
            "Day2: 提案文テンプレを作る（200字）",
            "Day3: 1件応募する",
            "Day4: 実績になりそうな小案件を狙う",
            "Day5: 継続提案（次の一手）",
            "Day6: 単価UPの条件整理",
            "Day7: 週次振り返り→次週の3手",
        ],
        "influence": [
            "Day1: 発信テーマを1つ決める",
            "Day2: 自己紹介ポストを作る",
            "Day3: 1日1投稿×3日分を下書き",
            "Day4: 反応の良い型を真似る",
            "Day5: プロフィール整備",
            "Day6: 無料プレゼント案を作る",
            "Day7: 来週の投稿カレンダー作成",
        ],
        "attack": [
            "Day1: 売れてる商品を10個調査",
            "Day2: 仕入れ/販売チャネル候補を決める",
            "Day3: まず1商品を仮出品",
            "Day4: タイトル/画像/説明を改善",
            "Day5: 価格テスト（±10%）",
            "Day6: リピートできる仕組み化",
            "Day7: 数字の振り返り→継続判断",
        ],
        "build": [
            "Day1: 解決したい悩みを1つに絞る",
            "Day2: 入力→出力の1画面を設計",
            "Day3: 最小機能で実装（動くが正義）",
            "Day4: 使い方ページを作る",
            "Day5: 課金導線（Premium）を整える",
            "Day6: ユーザーの声を1件取る",
            "Day7: 次の改善3点を決める",
        ],
    }.get(result_type, [])

    y = height - 170
    c.setFont("IPAexGothic", 13)
    for line in roadmap:
        c.drawString(50, y, f"・{line}")
        y -= 22
        if y < 60:
            c.showPage()
            c.setFont("IPAexGothic", 13)
            y = height - 60

    c.showPage()
    c.save()

    pdf = buf.getvalue()
    buf.close()
    return pdf


@login_required
def premium_download_dynamic(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return redirect("premium_page")  # or premium_required page

    # 最新の診断結果でタイプを決める（必要ならpk指定版にしてもOK）
    d = Diagnosis.objects.filter(user=request.user).order_by("-id").first()
    if not d:
        return redirect("diagnosis_start")

    display_name = request.user.get_full_name() or request.user.username
    pdf_bytes = _build_roadmap_pdf(display_name, d.result_type)

    filename = f"{d.result_type}_7day_roadmap_{request.user.username}.pdf"
    return FileResponse(
        BytesIO(pdf_bytes),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )