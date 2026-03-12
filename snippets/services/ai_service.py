from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_ai_reply(prompt):

    response = client.responses.create(
        model="gpt-5.4",
        input=prompt
    )

    return response.output_text

def ask_ai(question):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "あなたは副業コーチです"},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content

def generate_roadmap(question):

    prompt = f"""
あなたは副業コーチです。
初心者でもできる副業ロードマップを作ってください。

質問:
{question}
"""

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            #{"role": "system", "content": "あなたは優秀な副業コーチです"},
            {"role": "user", "content": prompt},
        ],

    )

    return response.choices[0].message.content

def ai_coach(question):

    prompt = f"""
あなたは優秀な副業コーチです。

ユーザーの状況に合わせて
副業アドバイスをしてください。

・初心者向け
・具体的
・行動プラン

ユーザー質問
{question}
"""
    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {"role": "system", "content": "あなたは副業コーチです"},
                {"role": "user", "content": question},
            ],
        )

        answer = response.choices[0].message.content

        return answer

    except Exception as e:

        print(e)

        return "AIエラーが発生しました。APIキーまたはクォータを確認してください。"

def ai_template(topic):

    prompt = f"""
副業初心者向けに
使えるテンプレートを作ってください

テーマ
{topic}
"""

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {"role": "system", "content": "副業コーチ"},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content