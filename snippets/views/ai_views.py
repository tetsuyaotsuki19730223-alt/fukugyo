from openai import OpenAI
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.services.ai_service import generate_roadmap

client = OpenAI(api_key=settings.OPENAI_API_KEY or "")


@login_required
def ai_chat(request):

    answer = "現在AIチャットはメンテナンス中です。"

    return render(
        request,
        "snippets/ai_chat.html",
        {"answer": answer}
    )


def ai_blog_generator(request):
    return render(request, "snippets/ai_blog.html")


def ai_roadmap(request):

    user_type = request.GET.get("type")

    roadmap = generate_roadmap(user_type)

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

    return render(request, "snippets/roadmap_result.html", {"roadmap": roadmap})


def ai_report(request):

    report = {
        "type": "Influencer型",

        "jobs": [
            "AIブログ",
            "SNS発信",
            "note販売"
        ],

        "roadmap": [
            "Week1 ジャンル決定",
            "Week2 SNS開始",
            "Week3 AI記事投稿",
            "Week4 案件応募"
        ]
    }

    return render(
        request,
        "snippets/ai_report.html",
        {"report": report}
    )
