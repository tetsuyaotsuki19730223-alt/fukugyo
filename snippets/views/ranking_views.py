from django.shortcuts import render


def ranking(request):

    jobs = [

        {
            "name": "AIブログ",
            "income": "月5万〜30万",
            "difficulty": "低",
            "description": "ChatGPTで記事作成して広告収益"
        },

        {
            "name": "AIライター",
            "income": "月3万〜20万",
            "difficulty": "低",
            "description": "AIで記事作成して案件受注"
        },

        {
            "name": "SNS運用",
            "income": "月1万〜50万",
            "difficulty": "中",
            "description": "InstagramやXを育てて収益化"
        },

        {
            "name": "AI画像販売",
            "income": "月1万〜15万",
            "difficulty": "低",
            "description": "AI画像を販売"
        },

    ]

    return render(
        request,
        "snippets/sidejob_ranking.html",
        {"jobs": jobs}
    )