from django.shortcuts import render, redirect


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
        answer = request.POST.get("answer", "").strip()

        if not answer:
            return render(request, "snippets/type_diagnosis.html", {
                "error": "選択してください"
            })

        type_map = {
            "seller": {
                "type": "Seller型",
                "description": "営業・販売・提案で強みを発揮しやすいタイプです。",
                "jobs": [
                    "営業代行",
                    "物販",
                    "セールスライター",
                ],
                "first_action": "まずは売れる商品・サービスのリサーチから始めるのがおすすめです。"
            },
            "build": {
                "type": "Build型",
                "description": "作ること・仕組み化・積み上げで伸びやすいタイプです。",
                "jobs": [
                    "AIブログ",
                    "Web制作",
                    "アプリ開発",
                ],
                "first_action": "まずは小さく1つ作って公開するのがおすすめです。"
            },
            "influence": {
                "type": "Influence型",
                "description": "発信・影響力・コンテンツ販売で伸びやすいタイプです。",
                "jobs": [
                    "SNS発信",
                    "note販売",
                    "コンテンツ販売",
                ],
                "first_action": "まずは発信テーマを1つ決めるのがおすすめです。"
            },
            "stable": {
                "type": "Stable型",
                "description": "安定的にコツコツ継続して成果を出しやすいタイプです。",
                "jobs": [
                    "データ入力",
                    "事務代行",
                    "継続案件",
                ],
                "first_action": "まずは継続できる案件を1つ選ぶのがおすすめです。"
            },
        }

        result = type_map.get(answer, {
            "type": "Stable型",
            "description": "安定的にコツコツ進める副業と相性が良いタイプです。",
            "jobs": [
                "データ入力",
                "事務代行",
                "継続案件",
            ],
            "first_action": "まずは継続できる案件を1つ選ぶのがおすすめです。"
        })

        return render(request, "snippets/type_result.html", {
            "result": result,
            "answer": answer,
        })

    return render(request, "snippets/type_diagnosis.html")


def history(request):
    return render(request, "snippets/history.html")


def roadmap_result(request):
    return render(request, "snippets/roadmap_result.html")