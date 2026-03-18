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

    free_limit = 3

    # 無料ユーザーだけ制限
    if not profile.is_premium and profile.ai_count >= free_limit:
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
                        {
                            "role": "system",
                            "content": "あなたは副業コーチです。初心者にもわかりやすく、具体的に回答してください。"
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    max_tokens=max_tokens,
                    timeout=15
                )

                answer = response.choices[0].message.content

                # 無料ユーザーだけカウントアップ
                if not profile.is_premium:
                    profile.ai_count += 1
                    profile.save()

            except Exception as e:
                answer = f"AIエラー: {e}"

    remaining = max(0, free_limit - profile.ai_count)

    return render(request, "snippets/ai_chat.html", {
        "answer": answer,
        "question": question,
        "remaining": remaining,
        "is_premium": profile.is_premium,
    })

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
    user_type = request.GET.get("type", "").strip()

    if user_type == "seller":
        report = {
            "type": "Seller型",
            "jobs": ["営業代行", "物販", "セールスライター"],
            "roadmap": [
                "Week1 売れるジャンルを決める",
                "Week2 商品・サービスを調査する",
                "Week3 SNSや営業文を作る",
                "Week4 初案件応募"
            ]
        }

    elif user_type == "build":
        report = {
            "type": "Build型",
            "jobs": ["AIブログ", "Web制作", "アプリ開発"],
            "roadmap": [
                "Week1 作るテーマを決める",
                "Week2 ツールを準備する",
                "Week3 試作品を作る",
                "Week4 公開して反応を見る"
            ]
        }

    elif user_type == "influence":
        report = {
            "type": "Influence型",
            "jobs": ["SNS発信", "note販売", "コンテンツ販売"],
            "roadmap": [
                "Week1 発信テーマを決める",
                "Week2 SNS開始",
                "Week3 投稿を増やす",
                "Week4 商品導線を作る"
            ]
        }

    elif user_type == "stable":
        report = {
            "type": "Stable型",
            "jobs": ["データ入力", "事務代行", "継続案件"],
            "roadmap": [
                "Week1 継続しやすい副業を選ぶ",
                "Week2 プロフィール作成",
                "Week3 小案件に応募",
                "Week4 継続案件を狙う"
            ]
        }

    else:
        report = {
            "type": "未診断",
            "jobs": [],
            "roadmap": []
        }

    return render(request, "snippets/ai_report.html", {
        "report": report,
        "user_type": user_type,
    })