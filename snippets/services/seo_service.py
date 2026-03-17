from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_seo_article(keyword):

    prompt = f"""
    「{keyword}」でSEO記事を書いてください。

    ・3000文字以上
    ・見出しあり
    ・初心者向け
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content