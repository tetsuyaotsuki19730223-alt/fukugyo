from openai import OpenAI
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from snippets.models import Profile
from datetime import date

client = OpenAI(api_key=settings.OPENAI_API_KEY)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY or "")


@login_required
def ai_chat(request):

    profile = request.user.profile

    answer = ""
    question = ""

    # 🔥 GETでも落ちないように初期化しておく
    # ↑これが今回のエラー対策の本質

    if request.method == "POST":

        question = request.POST.get("question", "")

        if question:  # 空送信対策
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": question}
                    ],
                    max_tokens=500,
                    timeout=15
                )

                answer = response.choices[0].message.content

                # ✅ 回数カウント（無料ユーザーのみ）
                if not profile.is_premium:
                    profile.ai_count += 1
                    profile.save()

            except Exception as e:
                answer = f"AIエラー: {e}"

    return render(request, "snippets/ai_chat.html", {
        "answer": answer,
        "question": question
    })

def ai_blog_generator(request):
    return render(request, "snippets/ai_blog.html")


def ai_roadmap(request):

    roadmap = [
        "Week1 市場リサーチ",
        "Week2 SNS開始",
        "Week3 AIブログ作成",
        "Week4 初案件応募"
    ]

    return render(
        request,
        "snippets/ai_roadmap.html",
        {"roadmap": roadmap}
    )


def roadmap_result(request):

    roadmap = [
        "Week1 市場リサーチ",
        "Week2 SNS開始",
        "Week3 AIブログ作成",
        "Week4 初案件応募"
    ]

    return render(
        request,
        "snippets/roadmap_result.html",
        {"roadmap": roadmap}
    )


def ai_report(request):

    report = {
        "type": "Influencer型",

        "jobs": [
            "AIブログ",
            "SNS発信",
            "note販売"
        ],

        "income": "月5〜30万円",

        "roadmap": [
            "Week1 ジャンル決定",
            "Week2 SNS開始",
            "Week3 AI記事投稿",
            "Week4 初案件応募"
        ]
    }

    return render(
        request,
        "snippets/ai_report.html",
        {"report": report}
    )