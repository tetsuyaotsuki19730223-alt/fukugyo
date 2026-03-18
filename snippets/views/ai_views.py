from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from openai import OpenAI

from snippets.models import Profile
from snippets.services.ai_service import generate_roadmap

client = OpenAI(api_key=settings.OPENAI_API_KEY or "")


@login_required
def ai_chat(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    limit = 3

    if not profile.is_premium and profile.ai_count >= limit:
        return redirect("pricing")

    answer = ""
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            answer = "質問を入力してください"
        else:
            try:
                max_tokens = 800 if profile.is_premium else 200

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "あなたは副業コーチです"},
                        {"role": "user", "content": question},
                    ],
                    max_tokens=max_tokens,
                    timeout=15,
                )

                answer = response.choices[0].message.content

                if not profile.is_premium:
                    profile.ai_count += 1
                    profile.save()

            except Exception as e:
                answer = f"AIエラー: {e}"

    remaining = max(0, limit - profile.ai_count)

    return render(
        request,
        "snippets/ai_chat.html",
        {
            "answer": answer,
            "question": question,
            "remaining": remaining,
            "is_premium": profile.is_premium,
        },
    )


@login_required
def ai_roadmap(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    user_type = request.GET.get("type", "").strip()

    if not user_type:
        roadmap = "タイプが指定されていません。"
    else:
        try:
            roadmap = generate_roadmap(user_type)
        except Exception as e:
            roadmap = f"AIエラー: {e}"

    return render(
        request,
        "snippets/ai_roadmap.html",
        {
            "roadmap": roadmap,
            "is_premium": profile.is_premium,
        },
    )


def ai_blog_generator(request):
    return render(request, "snippets/ai_blog.html")


def roadmap_result(request):
    roadmap = [
        "Week1 市場リサーチ",
        "Week2 SNS開始",
        "Week3 AIブログ作成",
        "Week4 初案件応募",
    ]

    return render(request, "snippets/roadmap_result.html", {"roadmap": roadmap})


def ai_report(request):
    report = {
        "type": "Influencer型",
        "jobs": ["AIブログ", "SNS発信", "note販売"],
        "roadmap": [
            "Week1 ジャンル決定",
            "Week2 SNS開始",
            "Week3 AI記事投稿",
            "Week4 案件応募",
        ],
    }

    return render(request, "snippets/ai_report.html", {"report": report})