from django.shortcuts import render


def ai_sidejobs(request):

    jobs = [

        {
            "name": "AIブログ",
            "income": "月5万〜30万",
            "difficulty": "低"
        },

        {
            "name": "AIライター",
            "income": "月3万〜20万",
            "difficulty": "低"
        },

        {
            "name": "SNS運用",
            "income": "月1万〜50万",
            "difficulty": "中"
        },

        {
            "name": "AI画像販売",
            "income": "月1万〜15万",
            "difficulty": "低"
        },

        {
            "name": "AI動画作成",
            "income": "月3万〜40万",
            "difficulty": "中"
        },

    ]

    return render(
        request,
        "snippets/ai_sidejobs.html",
        {"jobs": jobs}
    )