from django.shortcuts import render


def templates(request):

    templates = [

        {
            "title": "AIブログテンプレ",
            "price": 980,
            "description": "AIでブログを書くテンプレ"
        },

        {
            "title": "SNS投稿テンプレ",
            "price": 980,
            "description": "フォロワーを増やす投稿テンプレ"
        },

        {
            "title": "副業ロードマップ",
            "price": 1980,
            "description": "副業を始めるロードマップ"
        },

    ]

    return render(
        request,
        "snippets/templates.html",
        {"templates": templates}
    )