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

形式

Week1
Week2
Week3
Week4
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        roadmap = response.choices[0].message.content

    return render(
        request,
        "snippets/ai_roadmap_generator.html",
        {"roadmap": roadmap}
    )