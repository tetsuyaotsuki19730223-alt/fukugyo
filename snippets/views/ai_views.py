from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY or "")


@login_required
def ai_chat(request):

    profile, _ = Profile.objects.get_or_create(user=request.user)

    limit = 3

    if not profile.is_premium and profile.level < 3:
        return render(request, "snippets/ai_chat.html", {
            "answer": "レベル3で解放されます🔥"
        })

    # ===================================
    # 🔥 ① 制限チェック（ここが最重要）
    # ===================================
    if not profile.is_premium:
        if profile.ai_count >= limit:
            return redirect("pricing")

    answer = ""
    question = ""

    # ===================================
    # 🔥 ② POST処理（AI実行）
    # ===================================
    if request.method == "POST":

        question = request.POST.get("question", "")

        if question:

            try:
                # 🔥 プレミアムで性能差
                if profile.is_premium:
                    max_tokens = 800
                else:
                    max_tokens = 200

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": question}
                    ],
                    max_tokens=max_tokens,
                    timeout=15
                )

                answer = response.choices[0].message.content

                # ===================================
                # 🔥 ③ 回数カウント（無料のみ）
                # ===================================
                if not profile.is_premium:
                    profile.ai_count += 1
                    profile.save()

            except Exception as e:
                answer = f"AIエラー: {e}"

        else:
            answer = "質問を入力してください"

    # ===================================
    # 🔥 ④ 残り回数表示
    # ===================================
    remaining = max(0, limit - profile.ai_count)

    return render(request, "snippets/ai_chat.html", {
        "answer": answer,
        "question": question,
        "remaining": remaining
    })

def ai_blog_generator(request):
    if profile.level < 7:
        return render(request, "snippets/ai_blog.html", {
            "error": "レベル7で解放🔥"
        })


def ai_roadmap(request):

    if profile.level < 5:
        return render(request, "snippets/ai_roadmap.html", {
            "roadmap": "レベル5で解放🔥"
        })


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