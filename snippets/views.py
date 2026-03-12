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

stripe.api_key = settings.STRIPE_SECRET_KEY
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def landing(request):

    if request.user.is_authenticated:

        profile = Profile.objects.get(user=request.user)

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

def calculate_level(xp):

    return xp // 100 + 1

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

    users = Profile.objects.order_by("-xp")[:20]

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

        response = openai.ChatCompletion.create(
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

        response = openai.ChatCompletion.create(

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


@login_required
def dashboard(request):

    profile = request.user.profile

    mission = Mission.objects.first()

    context = {
        "profile": profile,
        "mission": mission,
    }

    return render(
        request,
        "snippets/dashboard.html",
        context
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

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
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

def diagnosis_share_image(request):

    result = request.GET.get("result")

    img = Image.new("RGB", (800, 400), color=(255, 255, 255))

    draw = ImageDraw.Draw(img)

    text = f"あなたの副業タイプ\n{result}"

    draw.text((100, 150), text, fill=(0, 0, 0))

    response = HttpResponse(content_type="image/png")

    img.save(response, "PNG")

    return response

def sidejob_list(request):

    jobs = SideJob.objects.all()

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

        response = openai.ChatCompletion.create(

            model="gpt-4o-mini",

            messages=[
                {"role": "user", "content": prompt}
            ]

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

    checkout_session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=[
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],

        mode="subscription",

        success_url="http://localhost:8000/premium/",

        cancel_url="http://localhost:8000/pricing/",

    )

    return redirect(checkout_session.url)

def pricing(request):

    return render(request, "snippets/pricing.html")


def premium_page(request):

    return render(request, "snippets/premium.html")

def diagnosis(request):

    answer = None

    if request.method == "POST":

        question = request.POST.get("question")

        if not request.user.is_authenticated:

            count = request.session.get("free_ai_count", 0)

            print("現在の回数:", count)  # ←確認用

            if count >= 3:

                answer = "無料利用は3回までです。ログインすると続きが利用できます。"

                return render(
                    request,
                    "snippets/diagnosis.html",
                    {"answer": answer},
                )

            request.session["free_ai_count"] = count + 1
            request.session.modified = True

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
        {"answer": answer},
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

    return render(
        request,
        "snippets/home.html"
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
"""

        idea = generate_roadmap(prompt)

    return render(
        request,
        "snippets/idea.html",
        {"idea": idea},
    )