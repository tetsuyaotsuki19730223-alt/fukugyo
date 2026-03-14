from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Profile, CoachMission, DiagnosisResult, Mission
from .forms import SignupForm
from openai import OpenAI
from django.conf import settings
from datetime import date
import stripe
from django.http import JsonResponse
from .models import Diagnosis
from .models import Referral
from .models import Roadmap
from .models import AIChat
from datetime import timedelta
from .models import DailyMission
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from .models import CommunityPost
from .models import Profile
from .services.ai_service import generate_roadmap
from .models import Diagnosis
from .services.ai_service import ai_coach
from django.contrib.auth.models import AnonymousUser
import json
from .models import SideJob
from PIL import Image, ImageDraw, ImageFont
import os

stripe.api_key = settings.STRIPE_SECRET_KEY
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def calculate_level(xp):

    return xp // 100 + 1

def landing(request):

    if request.user.is_authenticated:

        profile = request.user.profile
        profile.xp += 10
        profile.level = calculate_level(profile.xp)
        profile.save()

        mission = CoachMission.objects.order_by("?").first()

        streak = profile.streak

    else:

        mission = None
        streak = 0

    return render(
        request,
        "snippets/landing.html",
        {
            "mission": mission,
            "streak": streak,
        },
    )

def signup_view(request):

    ref_code = request.GET.get("ref")

    if ref_code:

        try:

            ref = Referral.objects.get(code=ref_code)

            ref.invited_count += 1
            ref.save()

            profile = Profile.objects.get(user=ref.user)

            profile.xp += 50
            profile.save()

        except Referral.DoesNotExist:

            pass

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            Referral.objects.create(user=user)

            return redirect("login")

    else:

        form = SignupForm()

    return render(request, "snippets/signup.html", {"form": form})


@login_required
def today_mission(request):

    today = date.today()

    mission = DailyMission.objects.filter(
        user=request.user,
        created_at=today
    ).first()

    if not mission:

        prompt = """
副業初心者向けの今日やるタスクを3つ作ってください。

条件
・30分以内
・AIツールを使う
・副業につながる
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
        あなたは優秀な副業コーチです。

        ユーザーの状況を分析して
        副業ロードマップを作ってください。

        出力形式：

        【おすすめ副業】

        【理由】

        【30日ロードマップ】

        STEP1
        STEP2
        STEP3
        STEP4
        """
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )

        content = response.choices[0].message.content

        mission = DailyMission.objects.create(

            user=request.user,
            content=content

        )

    return render(

        request,
        "snippets/today_mission.html",
        {"mission": mission}

    )


@login_required
def mission_complete(request):

    profile = Profile.objects.get(user=request.user)

    mission = CoachMission.objects.first()

    if mission:

        profile.xp += mission.xp_reward

        profile.level = calculate_level(profile.xp)

        profile.save()

    return redirect("home")

def ranking(request):

    users = Profile.objects.order_by("-xp")[:50]

    return render(
        request,
        "snippets/ranking.html",
        {"users": users}
    )


@login_required
def diagnosis_start(request):

    answer = None

    if request.method == "POST":

        question = request.POST.get("question")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは副業コーチです。初心者に最適な副業を提案してください。"},
                {"role": "user", "content": question},
            ],
        )

        answer = response.choices[0].message.content

        AIChat.objects.create(
            user=request.user,
            question=question,
            answer=answer
        )

    return render(request, "snippets/diagnosis.html", {"answer": answer})

def diagnosis_result(request):

    result = {
        "title": "AIクリエイター型",
        "description": "AIを活用して副業を伸ばすタイプです"
    }

    AIChat.objects.create(

        user=request.user,
        question=question,
        answer=answer

    )    
    return redirect("diagnosis_result")


def ai_roadmap(request):

    roadmap = None

    if request.method == "POST":

        skill = request.POST.get("skill")
        time = request.POST.get("time")

        prompt = f"""
        あなたは副業コーチです。

        ユーザー条件

        スキル: {skill}
        副業時間: {time}

        副業ロードマップを作ってください。

        出力形式

        1ヶ月目
        2ヶ月目
        3ヶ月目
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        roadmap = response.choices[0].message.content

        Roadmap.objects.create(

            user=request.user,
            content=roadmap

        )

    return render(
        request,
        "snippets/roadmap.html",
        {"roadmap": roadmap}
    )

def create_checkout_session(request):

    session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=[{
            "price": settings.STRIPE_PRICE_ID,
            "quantity": 1,
        }],

        mode="subscription",

        success_url=settings.SITE_URL + "/premium/",

        cancel_url=settings.SITE_URL + "/pricing/",
    )

    return JsonResponse({"id": session.id})



def ai_coach(request):

    answer = None

    if request.method == "POST":

        question = request.POST.get("question")

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {"role": "user", "content": question}
            ]

        )

        answer = response.choices[0].message.content

        AIChat.objects.create(

            user=request.user,
            question=question,
            answer=answer

        )

    chats = AIChat.objects.filter(user=request.user).order_by("created_at")

    return render(

        request,
        "snippets/ai_coach.html",

        {
            "answer": answer,
            "chats": chats
        }

    )


def dashboard(request):

    profile = request.user.profile

    referral = Referral.objects.get(user=request.user)

    referral_link = request.build_absolute_uri(
        "/signup/?ref=" + referral.code
    )

    return render(
        request,
        "snippets/dashboard.html",
        {
            "profile": profile,
            "referral_link": referral_link
        }
    )

@login_required
def ai_sidejob_ideas(request):

    ideas = None

    if request.method == "POST":

        skill = request.POST.get("skill")
        interest = request.POST.get("interest")

        prompt = f"""
あなたは副業コーチです。

ユーザー情報
スキル: {skill}
興味: {interest}

副業アイデアを5個提案してください。

出力形式

副業名
内容
最初の行動
収益化方法
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": question}
            ],
        )

        ideas = response.choices[0].message.content

    return render(
        request,
        "snippets/ideas.html",
        {"ideas": ideas}
    )


@login_required
def ai_chat_history(request):

    chats = AIChat.objects.filter(user=request.user).order_by("-created_at")

    return render(

        request,
        "snippets/ai_history.html",
        {"chats": chats}

    )

def download_roadmap_pdf(request):

    roadmap = Roadmap.objects.filter(
        user=request.user
    ).last()

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = 'attachment; filename="roadmap.pdf"'

    p = canvas.Canvas(response)

    text = p.beginText(50, 800)

    text.setFont("Helvetica", 12)

    lines = roadmap.content.split("\n")

    for line in lines:

        text.textLine(line)

    p.drawText(text)

    p.showPage()

    p.save()

    return response

from PIL import Image, ImageDraw
from django.http import HttpResponse


def diagnosis_share_image(request):

    result = request.GET.get("result", "副業タイプ")

    # 画像作成
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))

    draw = ImageDraw.Draw(img)

    text = f"あなたの副業タイプ\n\n{result}\n\nAI副業大学"

    draw.text((100, 150), text, fill=(0, 0, 0))

    response = HttpResponse(content_type="image/png")

    img.save(response, "PNG")

    return response

def sidejob_list(request):

    jobs = SideJob.objects.all().order_by("-income_max")

    return render(
        request,
        "snippets/sidejob_list.html",
        {"jobs": jobs}
    )

@login_required
def apply_sidejob(request, job_id):

    job = SideJob.objects.get(id=job_id)

    SideJobApply.objects.create(

        job=job,
        user=request.user

    )

    return redirect("sidejob_list")

@login_required
def ai_blog_generator(request):

    article = None

    if request.method == "POST":

        topic = request.POST.get("topic")

        prompt = f"""
副業ブログ記事を書いてください

テーマ
{topic}

構成

タイトル
導入
見出し3つ
まとめ
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": question}
            ],
        )

        article = response.choices[0].message.content

    return render(
        request,
        "snippets/ai_blog.html",
        {"article": article}
    )


@login_required
def community(request):

    if request.method == "POST":

        content = request.POST.get("content")

        CommunityPost.objects.create(

            user=request.user,
            content=content

        )

    posts = CommunityPost.objects.order_by("-created_at")

    return render(

        request,
        "snippets/community.html",
        {"posts": posts}

    )

def template_market(request):

    templates = Template.objects.all()

    return render(

        request,
        "snippets/template_market.html",

        {"templates": templates}

    )

@login_required
def buy_template(request, template_id):

    template = Template.objects.get(id=template_id)

    TemplatePurchase.objects.create(

        template=template,
        user=request.user

    )

    return redirect("template_market")


def type_diagnosis(request):

    result = None
    description = None

    if request.method == "POST":

        q1 = request.POST.get("q1")
        q2 = request.POST.get("q2")
        q3 = request.POST.get("q3")

        score = {
            "発信型": 0,
            "スキル型": 0,
            "AI型": 0,
            "投資型": 0
        }

        if q1 == "A":
            score["発信型"] += 1
        else:
            score["スキル型"] += 1

        if q2 == "A":
            score["AI型"] += 1
        else:
            score["投資型"] += 1

        if q3 == "A":
            score["発信型"] += 1
        else:
            score["スキル型"] += 1

        result = max(score, key=score.get)

        type_text = {
            "発信型": "SNSやYouTubeなど発信系の副業が向いています。",
            "スキル型": "プログラミングやデザインなどスキル副業が向いています。",
            "AI型": "AIツールを使った副業が向いています。",
            "投資型": "資産運用型の副業が向いています。",
        }

        description = type_text[result]

    return render(
        request,
        "snippets/type_diagnosis.html",
        {
            "result": result,
            "description": description,
        },
    )

def type_result(request):

    q1 = request.POST.get("q1")
    q2 = request.POST.get("q2")
    q3 = request.POST.get("q3")

    score = 0

    if q1 == "challenge":
        score += 1

    if q2 == "create":
        score += 1

    if q3 == "ai":
        score += 1

    if score >= 2:
        result = "AI活用型"
        advice = "AIを使った副業（AIライティング、AIツール開発）が向いています。"

    else:
        result = "職人型"
        advice = "スキル型副業（プログラミング、デザイン、動画編集）が向いています。"

    return render(
        request,
        "snippets/type_result.html",
        {
            "result": result,
            "advice": advice,
        },
    )


def create_checkout(request):

    session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=[{
            "price": settings.STRIPE_PRICE_ID,
            "quantity": 1,
        }],

        mode="subscription",

        success_url=settings.SITE_URL + "/premium/",
        cancel_url=settings.SITE_URL + "/pricing/",
    )

    return redirect(session.url)

def pricing(request):

    return render(request, "snippets/pricing.html")


def premium_page(request):

    return render(request, "snippets/premium.html")

def diagnosis(request):

    answer = None

    # 無料回数
    free_remaining = None

    if not request.user.is_authenticated:

        count = request.session.get("free_ai_count", 0)

        free_remaining = max(0, 3 - count)

    if request.method == "POST":

        question = request.POST.get("question")

        if question:

            if not request.user.is_authenticated:

                count = request.session.get("free_ai_count", 0)

                if count >= 3:

                    answer = "無料利用は3回までです。ログインすると続きが利用できます。"

                    return render(
                        request,
                        "snippets/diagnosis.html",
                        {
                            "answer": answer,
                            "free_remaining": 0
                        },
                    )

                request.session["free_ai_count"] = count + 1

                free_remaining = 3 - (count + 1)

            answer = generate_roadmap(question)

            if request.user.is_authenticated:

                AIChat.objects.create(
                    user=request.user,
                    question=question,
                    answer=answer
                )

    return render(
        request,
        "snippets/diagnosis.html",
        {
            "answer": answer,
            "free_remaining": free_remaining
        },
    )

@login_required
def ai_chat(request):

    answer = None
    question = None

    if request.method == "POST":

        question = request.POST.get("question")

        answer = ai_coach(question)

        AIChat.objects.create(

            user=request.user,
            question=question,
            answer=answer

        )

    return render(
        request,
        "snippets/ai_chat.html",
        {"answer": answer}
    )

@login_required
def template_generator(request):

    result = None

    if request.method == "POST":

        topic = request.POST.get("topic")

        result = ai_template(topic)

    return render(
        request,
        "snippets/template.html",
        {"result": result}
    )


def income_simulator(request):

    result = None

    if request.method == "POST":

        hours = int(request.POST.get("hours"))

        income = hours * 1000 * 20

        result = income

    return render(
        request,
        "snippets/income.html",
        {"result": result}
    )


def home(request):

    user_count = User.objects.count()

    return render(
        request,
        "snippets/home.html",
        {"user_count": user_count}
    )

@login_required
def history(request):

    chats = AIChat.objects.filter(user=request.user).order_by("-created_at")

    return render(

        request,
        "snippets/history.html",
        {"chats": chats},

    )

def idea(request):

    idea = None

    if request.method == "POST":

        skill = request.POST.get("skill")

        prompt = f"""
ユーザーのスキル

{skill}

この人におすすめの副業アイデアを
5つ提案してください。

最後に以下の注意書きを必ず入れてください。

※副業の成果は個人差があります。
"""

        idea = generate_roadmap(prompt)

    return render(
        request,
        "snippets/idea.html",
        {"idea": idea},
    )

def stripe_webhook(request):

    payload = request.body

    event = None

    try:

        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )

    except ValueError:

        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        email = session["customer_details"]["email"]

        from django.contrib.auth.models import User

        user = User.objects.get(email=email)

        profile = user.profile

        profile.is_premium = True

        profile.save()

    return HttpResponse(status=200)

def stripe_webhook(request):
    return HttpResponse(status=200)


def ai_search(request):

    result = None

    if request.method == "POST":

        query = request.POST.get("query")

        prompt = f"""
ユーザー検索

{query}

この人におすすめの副業を
5つ提案してください。

形式

副業名
理由
収益目安
"""

        result = ai_coach(prompt)

    return render(
        request,
        "snippets/ai_search.html",
        {"result": result},
    )

def success_list(request):

    stories = SuccessStory.objects.all()

    return render(
        request,
        "snippets/success.html",
        {"stories": stories}
    )


def sidejob_detail(request, id):

    job = SideJob.objects.get(id=id)

    return render(
        request,
        "snippets/sidejob_detail.html",
        {"job": job}
    )

def sidejob_ranking(request):

    jobs = SideJob.objects.order_by("-income_max")[:20]

    return render(
        request,
        "snippets/sidejob_ranking.html",
        {"jobs": jobs}
    )

def start_page(request):

    return render(
        request,
        "snippets/start.html"
    )

def dashboard_preview(request):

    context = {
        "level": 3,
        "xp": 230,
        "streak": 5
    }

    return render(
        request,
        "snippets/dashboard_preview.html",
        context
    )

def ai_diagnosis(request):

    result = None

    if request.method == "POST":

        skill = request.POST.get("skill")
        interest = request.POST.get("interest")
        time = request.POST.get("time")

        prompt = f"""
ユーザーの副業適性を診断してください。

スキル
{skill}

興味
{interest}

副業に使える時間
{time}

以下の形式で回答してください。

おすすめ副業
理由
最初のステップ

最後に以下の注意書きを必ず入れてください。

※副業の成果は個人差があります。
"""

        result = generate_roadmap(prompt)

    return render(
        request,
        "snippets/ai_diagnosis.html",
        {"result": result}
    )


def diagnosis_share_image(request):

    result = request.GET.get("result", "副業タイプ")

    # 画像サイズ
    width = 800
    height = 450

    # 背景
    img = Image.new("RGB", (width, height), color=(30, 30, 30))

    draw = ImageDraw.Draw(img)

    font_path = os.path.join(
        "fonts",
        "NotoSansJP-Bold.ttf"
    )

    title_font = ImageFont.truetype(font_path, 40)
    result_font = ImageFont.truetype(font_path, 60)
    site_font = ImageFont.truetype(font_path, 30)

    # タイトル
    draw.text(
        (200, 80),
        "あなたの副業タイプ",
        fill=(255, 255, 255),
        font=title_font
    )

    # 結果
    draw.text(
        (200, 200),
        result,
        fill=(255, 200, 0),
        font=result_font
    )

    # サイト名
    draw.text(
        (220, 340),
        "AI副業大学",
        fill=(255, 255, 255),
        font=site_font
    )

    response = HttpResponse(content_type="image/png")

    img.save(response, "PNG")

    return response

def privacy(request):
    return render(request, "snippets/privacy.html")


def terms(request):
    return render(request, "snippets/terms.html")


def legal(request):
    return render(request, "snippets/legal.html")