from django.shortcuts import render, redirect
from snippets.models import Profile


def diagnosis(request):
    return render(request, "snippets/diagnosis.html")


def result(request):
    result = {
        "type": "Influencer型",
        "description": "SNS発信で収益化するタイプです"
    }

    return render(
        request,
        "snippets/result.html",
        {"result": result}
    )



def type_diagnosis(request):
    if request.method == "POST":
        answer = request.POST.get("answer")

        if not answer:
            return render(request, "snippets/type_diagnosis.html", {
                "error": "選択してください。"
            })

        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.sidejob_type = answer
            profile.save()

        results = {
            "seller": {
                "type": "SELLER",
                "description": "販売・提案・価値訴求が得意なタイプです。",
                "jobs": ["コンテンツ販売", "SNS運用代行", "オンライン営業"],
                "first_action": "誰に何を売るかを1文で書いてみましょう。",
            },
            "build": {
                "type": "BUILD",
                "description": "作る力・積み上げる力を活かしやすいタイプです。",
                "jobs": ["Web制作", "アプリ開発", "テンプレート販売"],
                "first_action": "作れそうなものを1つ決めてみましょう。",
            },
            "influence": {
                "type": "INFLUENCE",
                "description": "発信力・共感力・影響力を活かしやすいタイプです。",
                "jobs": ["SNS発信", "コミュニティ運営", "コンテンツ販売"],
                "first_action": "発信テーマを1つ決めてみましょう。",
            },
            "stable": {
                "type": "STABLE",
                "description": "堅実に継続しながら積み上げるのが得意なタイプです。",
                "jobs": ["事務代行", "データ入力", "ブログ運営"],
                "first_action": "10分でできる作業を1つ決めてみましょう。",
            },
        }

        result = results.get(answer)
        return render(request, "snippets/type_result.html", {"result": result})

    return render(request, "snippets/type_diagnosis.html")


def history(request):
    return render(request, "snippets/history.html")


def roadmap_result(request):
    return render(request, "snippets/roadmap_result.html")