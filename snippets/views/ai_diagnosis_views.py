from django.shortcuts import render
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ai_personal_diagnosis(request):

    result = None

    if request.method == "POST":

        skill = request.POST.get("skill")
        time = request.POST.get("time")
        goal = request.POST.get("goal")

        prompt = f"""
以下のユーザーに最適な副業を提案してください

スキル
{skill}

使える時間
{time}

目標
{goal}

回答形式

おすすめ副業
収益目安
始め方
"""

        try:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは副業コーチです"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )

            result = response.choices[0].message.content

        except Exception as e:

            result = f"AIエラー: {e}"

    return render(
        request,
        "snippets/ai_personal_diagnosis.html",
        {"result": result}
    )