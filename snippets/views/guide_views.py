from django.shortcuts import render


def sidejob_guide(request):

    steps = [

        {
            "title": "副業ジャンルを決める",
            "text": "AIブログ・SNS運用など自分に合う副業を決めます"
        },

        {
            "title": "小さく始める",
            "text": "1日30分〜1時間でスタートします"
        },

        {
            "title": "AIを活用する",
            "text": "ChatGPTなどAIを使うと効率が上がります"
        },

        {
            "title": "継続する",
            "text": "3ヶ月続けると結果が出やすくなります"
        },

    ]

    return render(
        request,
        "snippets/sidejob_guide.html",
        {"steps": steps}
    )