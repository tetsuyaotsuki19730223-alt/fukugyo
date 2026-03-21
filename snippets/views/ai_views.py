import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from openai import OpenAI

from snippets.models import Profile, AIChatHistory

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def free_reply_format(conclusion, reason, action, premium_note):
    return (
        f"結論：{conclusion}\n\n"
        f"理由：{reason}\n\n"
        f"次の一歩：{action}\n\n"
        f"{premium_note}"
    )


def build_free_chat_reply(user_message):
    message = (user_message or "").strip()

    if "何を" in message or "何から" in message or "始め" in message:
        return free_reply_format(
            conclusion="最初は『1つに絞って小さく始める』のがおすすめです。",
            reason="最初から選択肢を広げすぎると、迷って動けなくなりやすいからです。",
            action="今日中に、やってみたい副業を1つだけ決めてください。",
            premium_note="プレミアムでは、あなたに合う副業の選び方と具体的な始め方まで提案できます。"
        )

    elif "向いて" in message or "合う" in message:
        return free_reply_format(
            conclusion="あなたは『続けやすい副業』を基準に選ぶのが向いています。",
            reason="副業は才能より、継続できるかどうかで結果が変わりやすいからです。",
            action="興味がある副業を3つ書き出し、その中で一番続けやすそうなものを1つ選んでください。",
            premium_note="プレミアムでは、あなた向けに副業タイプをさらに深掘りして提案できます。"
        )

    elif "稼げ" in message or "収益" in message or "売上" in message:
        return free_reply_format(
            conclusion="早く稼ぐより、『小さく売れる形』を作ることが先です。",
            reason="最初は大きな収益より、最初の1件を作ることが重要だからです。",
            action="まずは『誰のどんな悩みを助けるか』を1文で書いてみてください。",
            premium_note="プレミアムでは、売れるテーマ設計まで具体化できます。"
        )

    elif "時間" in message or "忙しい" in message or "続か" in message:
        return free_reply_format(
            conclusion="時間がない場合は、『毎日10分で進む副業』から始めるのがおすすめです。",
            reason="負荷が高すぎると、良い副業でも継続しにくいからです。",
            action="今日やる作業を10分で終わる単位まで小さく分けてください。",
            premium_note="プレミアムでは、あなたの生活に合わせた継続プランまで提案できます。"
        )

    else:
        return free_reply_format(
            conclusion="今は『完璧に考える』より『小さく試す』ことが大事です。",
            reason="副業は考えるだけより、実際に動いた方が自分に合う方向が見えやすいからです。",
            action="今日できる行動を1つだけ決めて、10分だけ進めてみてください。",
            premium_note="プレミアムでは、あなた専用の具体的な進め方まで提案できます。"
        )


def build_premium_chat_reply(user_message):
    message = (user_message or "").strip()

    return (
        f"あなたの相談内容：{message}\n\n"
        "結論：今の段階では、相性が良さそうな副業を1つに絞って、短期間で試す進め方が最適です。\n\n"
        "理由：副業は最初から広げすぎると継続しにくく、結果が出る前に止まりやすいからです。"
        "一方で、1つに絞ると改善が早くなり、自分に合う型が見えやすくなります。\n\n"
        "おすすめの進め方：\n"
        "1. 取り組む副業を1つ決める\n"
        "2. 誰のどんな悩みを助けるかを明確にする\n"
        "3. 7日以内に小さな発信や出品を1回やる\n"
        "4. 反応を見て改善する\n\n"
        "今日の一歩：『誰に何を提供するか』を1文で書いてみてください。"
    )


def build_openai_reply(user_message, is_premium=False):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY が未設定です。")

    system_prompt = (
        "あなたは『AI副業コーチ』です。"
        "日本語で、実践的でわかりやすく回答してください。"
        "ユーザーが今日すぐ動ける内容を優先してください。"
    )

    if is_premium:
        instruction = (
            "プレミアム会員向けとして回答してください。"
            "構成は『結論』『理由』『具体策』『今日の一歩』。"
            "具体例を入れ、個別感を強くしてください。"
            "長さはやや長めで構いません。"
        )
    else:
        instruction = (
            "無料会員向けとして回答してください。"
            "構成は『結論』『理由』『次の一歩』。"
            "短くても完結した回答にしてください。"
            "文の途中で終わる印象を出さないでください。"
            "最後に一文だけ、プレミアムならさらに具体化できると自然に伝えてください。"
        )

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": instruction},
            {"role": "user", "content": user_message},
        ],
    )

    return response.output_text


@login_required
def ai_chat(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    reply = ""
    limit_message = ""

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if not user_message:
            reply = "メッセージを入力してください。"
        else:
            if not profile.is_premium and profile.ai_count >= 3:
                limit_message = "無料プランのAIチャットは3回までです。プレミアムで無制限に利用できます。"
            else:
                try:
                    reply = build_openai_reply(
                        user_message=user_message,
                        is_premium=profile.is_premium,
                    )
                except Exception:
                    if profile.is_premium:
                        reply = build_premium_chat_reply(user_message)
                    else:
                        reply = build_free_chat_reply(user_message)

                AIChatHistory.objects.create(
                    user=request.user,
                    question=user_message,
                    answer=reply
                )

                profile.ai_count += 1
                profile.save()

    return render(request, "snippets/ai_chat.html", {
        "reply": reply,
        "limit_message": limit_message,
        "ai_count": profile.ai_count,
        "is_premium": profile.is_premium,
    })

@login_required
def ai_report(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    sidejob_type = request.GET.get("type", "seller")

    reports = {
        "seller": {
            "title": "SELLERタイプ",
            "description": "販売・提案・価値訴求が得意なタイプです。",
            "jobs": ["コンテンツ販売", "SNS運用代行", "オンライン営業"],
            "roadmap": [
                "1週目：売れそうなテーマを3つ出す",
                "2週目：発信内容を10個作る",
                "3週目：小さく販売導線を作る",
                "4週目：反応を見て改善する",
            ],
        },
        "build": {
            "title": "BUILDタイプ",
            "description": "作る力・積み上げる力を活かしやすいタイプです。",
            "jobs": ["Web制作", "アプリ開発", "テンプレート販売"],
            "roadmap": [
                "1週目：作れるものを3つ洗い出す",
                "2週目：1つ作品を完成させる",
                "3週目：公開して反応を見る",
                "4週目：改善して再提示する",
            ],
        },
        "influence": {
            "title": "INFLUENCEタイプ",
            "description": "発信力・共感力・影響力を活かしやすいタイプです。",
            "jobs": ["SNS発信", "コミュニティ運営", "コンテンツ販売"],
            "roadmap": [
                "1週目：発信テーマを1つ決める",
                "2週目：毎日発信する",
                "3週目：反応が良いテーマを絞る",
                "4週目：商品導線を考える",
            ],
        },
        "stable": {
            "title": "STABLEタイプ",
            "description": "堅実に継続しながら積み上げるのが得意なタイプです。",
            "jobs": ["事務代行", "データ入力", "ブログ運営"],
            "roadmap": [
                "1週目：継続しやすい副業を1つ選ぶ",
                "2週目：毎日10分作業する",
                "3週目：作業記録をつける",
                "4週目：小さな改善を入れる",
            ],
        },
    }

    result = reports.get(sidejob_type, reports["seller"])

    return render(request, "snippets/ai_report.html", {
        "profile": profile,
        "sidejob_type": sidejob_type,
        "result": result,
    })