from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def success_stories(request):

    stories = [

        {
            "name": "田中さん",
            "job": "会社員",
            "sidejob": "AIブログ",
            "income": "月8万円",
            "story": "AIで記事を書き始めて3ヶ月で収益化できました"
        },

        {
            "name": "佐藤さん",
            "job": "主婦",
            "sidejob": "SNS運用",
            "income": "月5万円",
            "story": "1日1時間の副業で収入が増えました"
        },

        {
            "name": "山本さん",
            "job": "学生",
            "sidejob": "AIライター",
            "income": "月12万円",
            "story": "AIで記事作成して案件を受注しています"
        }

    ]

    return render(
        request,
        "snippets/success_stories.html",
        {"stories": stories}
    )


@login_required
def success(request):

    #profile = request.user.profile
    #profile.is_premium = True
    #profile.save()

    return render(request, "snippets/success.html")