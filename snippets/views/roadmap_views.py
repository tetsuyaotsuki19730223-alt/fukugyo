from django.shortcuts import render
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ai_roadmap_generator(request):

    roadmap = None

    if request.method == "POST":

        job = request.POST.get("job")

        prompt = f"""
副業初心者向けに
{job} を始める4週間ロードマップを作ってください。

条件
・必ず Week1〜Week4 を出力
・各Weekは3〜5行
・簡潔に書く
"""

        try:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "副業コーチとして回答してください"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.7
            )

            roadmap = response.choices[0].message.content

        except Exception as e:

            roadmap = f"AIエラー: {e}"

    return render(
        request,
        "snippets/ai_roadmap_generator.html",
        {"roadmap": roadmap}
    )