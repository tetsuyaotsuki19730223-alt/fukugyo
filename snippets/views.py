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

def get_roadmap_pdf_relpath(result_type: str) -> str:
    """
    static/premium/ 配下のPDFをタイプ別に探し、
    無ければ stable_7day_roadmap.pdf にフォールバックする。
    """
    safe = (result_type or "").strip()
    candidate = f"premium/{safe}_7day_roadmap.pdf"
    abs_path = os.path.join(settings.BASE_DIR, "static", candidate)

    if safe and os.path.exists(abs_path):
        return candidate

    return "premium/stable_7day_roadmap.pdf"

def diagnosis_start(request):
    if request.method == "POST":
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            d = form.save(commit=False)

            # ★ここが重要：匿名なら user を入れない
            if request.user.is_authenticated:
                d.user = request.user

            d.result_type = judge_result_type(form.cleaned_data)
            d.save()

            request.session["last_diagnosis_id"] = d.id
            return redirect("diagnosis_result", pk=d.pk)
    else:
        form = DiagnosisForm()

    return render(request, "snippets/diagnosis_form.html", {"form": form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Diagnosis

from django.http import Http404

def diagnosis_result(request, pk: int):
    # ログイン済みなら本人のだけ見せる
    if request.user.is_authenticated:
        d = get_object_or_404(Diagnosis, pk=pk, user=request.user)
    else:
        # 匿名なら「直前に自分が作った結果」だけ見せる
        last_id = request.session.get("last_diagnosis_id")
        if last_id != pk:
            raise Http404("Not found")
        d = get_object_or_404(Diagnosis, pk=pk)

    is_premium = (
        request.user.is_authenticated
        and hasattr(request.user, "profile")
        and request.user.profile.is_premium
    )

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


from django.shortcuts import redirect
@login_required
@require_POST
def create_checkout_session(request):
    print(f"[TRACK] checkout_start user={request.user.id}")
    print("EVENT: checkout_session_created")        
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

    success_url = request.build_absolute_uri(
        reverse("billing_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    cancel_url = request.build_absolute_uri(
        reverse("billing_cancel")
    )

    # ここで必ず session を作る（分岐させない）
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=profile.stripe_customer_id,
        line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return redirect(session.url, permanent=False)

import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def premium_page(request):
    if not request.user.profile.is_premium:
        return render(request, "snippets/premium_required.html")

    # 最新の診断結果を取得
    d = Diagnosis.objects.filter(user=request.user).order_by("-id").first()
    if not d:
        return redirect("diagnosis_start")

    # ★タイプ別PDFが無ければ stable にフォールバック
    pdf_relpath = get_roadmap_pdf_relpath(d.result_type)

    # テンプレで使う（staticのURLを組み立てるだけなら relpath で十分）
    return render(request, "snippets/premium.html", {"pdf_relpath": pdf_relpath})

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
    print(f"[TRACK] checkout_success user={request.user.id}")
    print("EVENT: checkout_success")
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
    pdf_relpath = get_roadmap_pdf_relpath(d.result_type)
    abs_path = os.path.join(settings.BASE_DIR, "static", pdf_relpath)
    return FileResponse(open(abs_path, "rb"), as_attachment=True, filename=os.path.basename(abs_path))

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
    font_path = Path(settings.BASE_DIR) / "snippets" / "static" / "fonts" / "ipaexg.ttf"
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

from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Diagnosis, DailyProgress
@login_required
def coach_dashboard(request):
    if not request.user.profile.is_premium:
        return redirect("premium_page")    
    
    d = Diagnosis.objects.filter(user=request.user).order_by("-id").first()
    result_type = d.result_type if d else "build"

    action_map = {
        "stable": "今日やる：クラウドソーシングで『自分ができる仕事』を3つ探してURLをメモ。",
        "influence": "今日やる：発信テーマを1つ決めて自己紹介ポストを100字で下書き。",
        "attack": "今日やる：売れている商品を10個リストアップして理由を1行で。",
        "build": "今日やる：入力→出力が1画面で完結するツール案を1つ書く。",
    }
    today_action = action_map.get(result_type, action_map["build"])

    today = date.today()
    from datetime import timedelta

    gap_message = None
    yesterday = today - timedelta(days=1)

    did_yesterday = DailyProgress.objects.filter(
        user=request.user,
        date=yesterday,
        completed=True
    ).exists()

    did_today = DailyProgress.objects.filter(
        user=request.user,
        date=today,
        completed=True
    ).exists()

    if not did_today:
        if not did_yesterday:
            gap_message = "昨日はチェックインがありませんでした。今日は“再開日”です。小さく1つだけやりましょう。"

    two_days_ago = today - timedelta(days=2)
    did_two_days_ago = DailyProgress.objects.filter(user=request.user, date=two_days_ago, completed=True).exists()

    if not did_today and (not did_yesterday) and (not did_two_days_ago):
        gap_message = "2日空きました。ここで戻れれば勝ちです。今日は“5分で終わる行動”だけにしましょう。"

    # 今日の進捗（なければ未完了扱い）
    prog, _ = DailyProgress.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={"action": today_action, "completed": False},
    )

    # streak算出：今日から遡って completed=True が連続している日数
    streak = 0
    cur = today
    while True:
        p = DailyProgress.objects.filter(user=request.user, date=cur, completed=True).first()
        if not p:
            break
        streak += 1
        cur = cur - timedelta(days=1)
    print(f"[TRACK] streak user={request.user.id} days={streak}")
    if streak == 2:
        special_message = "明日が分岐点です。ここを越えれば習慣になります。"
        special_message = None
    if streak == 0:
        special_message = "今日は『最初の1日目』です。完璧じゃなくてOK。まずチェックインだけ取りにいきましょう。"
    elif streak == 1:
        special_message = "2日目まで来ました。ここで続く人が一気に増えます。今日も小さく進めましょう。"
    elif streak == 2:
        special_message = "明日が分岐点（3日目）です。ここを越えると『習慣』になります。今日は軽くでOK。"
    elif streak >= 3:
        special_message = f"{streak}日連続です。もう勝ちパターンに入っています。次は『同じ時間にやる』を固定しましょう。"

    feedback = None
    if prog.completed and prog.reflection:
        if result_type == "build":
            feedback = "あなたは構築型。完璧にしようとして止まる傾向があります。小さく出すことを意識しましょう。"
        elif result_type == "stable":
            feedback = "あなたは安定型。今日の積み上げが将来の土台になります。焦らず続けましょう。"
        elif result_type == "attack":
            feedback = "あなたは攻撃型。勢いは強みですが、継続が鍵です。明日も同じ時間に動きましょう。"
        elif result_type == "influence":
            feedback = "あなたは影響力型。言語化できています。発信に落とし込めば価値になります。"

    return render(request, "snippets/coach_dashboard.html", {
        "result_type": result_type,
        "today_action": prog.action,
        "streak_days": streak,
        "today_completed": prog.completed,
        "feedback": feedback,
        "special_message": special_message,
        "gap_message": gap_message,
    })

@require_POST
@login_required
def coach_checkin(request):
    if not request.user.profile.is_premium:
        return redirect("premium_page")    

    today = date.today()

    d = Diagnosis.objects.filter(user=request.user).order_by("-id").first()
    result_type = d.result_type if d else "build"

    action_map = {
        "stable": "今日やる：クラウドソーシングで『自分ができる仕事』を3つ探してURLをメモ。",
        "influence": "今日やる：発信テーマを1つ決めて自己紹介ポストを100字で下書き。",
        "attack": "今日やる：売れている商品を10個リストアップして理由を1行で。",
        "build": "今日やる：入力→出力が1画面で完結するツール案を1つ書く。",
    }
    today_action = action_map.get(result_type, action_map["build"])

    prog, _ = DailyProgress.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={"action": today_action},
    )

    # 完了処理
    prog.completed = True

    # 振り返り保存
    reflection = request.POST.get("reflection")
    if reflection:
        prog.reflection = reflection

    prog.save()
    print(f"[TRACK] checkin user={request.user.id} date={today}")
    return redirect("coach_dashboard")

from django.db.models import Count
from datetime import date, timedelta
from .models import DailyProgress

@login_required
def coach_stats(request):
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    today_count = DailyProgress.objects.filter(
        date=today,
        completed=True
    ).values("user").distinct().count()

    yesterday_count = DailyProgress.objects.filter(
        date=yesterday,
        completed=True
    ).values("user").distinct().count()

    weekly_active = DailyProgress.objects.filter(
        date__gte=week_ago,
        completed=True
    ).values("user").distinct().count()

    max_streak = 0
    users = DailyProgress.objects.values("user").distinct()
    for u in users:
        user_id = u["user"]
        streak = 0
        cur = today
        while DailyProgress.objects.filter(
            user_id=user_id,
            date=cur,
            completed=True
        ).exists():
            streak += 1
            cur -= timedelta(days=1)
        max_streak = max(max_streak, streak)

    return render(request, "snippets/coach_stats.html", {
        "today_count": today_count,
        "yesterday_count": yesterday_count,
        "weekly_active": weekly_active,
        "max_streak": max_streak,
    })

from datetime import date, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.shortcuts import render

from .models import Profile

@staff_member_required
def billing_stats(request):
    User = get_user_model()

    total_users = User.objects.count()
    premium_users = Profile.objects.filter(is_premium=True).count()
    premium_rate = (premium_users / total_users * 100) if total_users else 0

    # 直近7日でPremium化（※Profileにupdated_atが無い場合は目安として「作成日」が取れないので雑になります）
    # もし Profile に created_at/updated_at が無いなら、この値は一旦出さない方が安全。
    # ここでは、まずは「総数」だけでOKにしておく。
    last7_premium = None

    return render(request, "snippets/billing_stats.html", {
        "total_users": total_users,
        "premium_users": premium_users,
        "premium_rate": round(premium_rate, 1),
        "last7_premium": last7_premium,
    })