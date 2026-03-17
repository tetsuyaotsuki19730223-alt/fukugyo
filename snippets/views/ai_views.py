from openai import OpenAI
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.models import Profile
from datetime import date

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@login_required
def ai_chat(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    answer = None

    if request.method == "POST":

        question = request.POST.get("question")

        try:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[

                    {
                        "role": "system",
                        "content": """
            あなたは副業コーチです。

            目的
            ユーザーが副業で稼げるようサポートする。

            回答ルール
            ・初心者にもわかりやすく
            ・副業アイデアを提案
            ・収益目安を書く
            ・最初の行動を提示

            回答形式

            おすすめ副業
            収益目安
            始め方
            """
                    },

                    {
                        "role": "user",
                        "content": question
                    }

                ],
                max_tokens=800,
                temperature=0.7
            )

            answer = response.choices[0].message.content

        except Exception as e:

            answer = f"AIエラー: {e}"

    return render(
        request,
        "snippets/ai_chat.html",
        {"answer": answer}
    )

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