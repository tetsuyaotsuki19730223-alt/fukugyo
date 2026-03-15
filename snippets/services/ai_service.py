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

def generate_roadmap(user_type):

    if user_type == "creator":

        return [
            "SNSアカウント作成",
            "AIで記事作成",
            "ブログ公開",
            "広告収益開始"
        ]

    if user_type == "builder":

        return [
            "副業テーマ決定",
            "Webサービス作成",
            "LP公開",
            "ユーザー獲得"
        ]

    if user_type == "seller":

        return [
            "商品ジャンル決定",
            "SNS発信開始",
            "EC販売開始",
            "広告運用"
        ]

    return [
        "副業リサーチ",
        "AI活用",
        "小さくスタート"
    ]


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