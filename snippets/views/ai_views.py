from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from django.conf import settings
from snippets.models import Profile

client = OpenAI(api_key=settings.OPENAI_API_KEY or "")


@login_required
def ai_chat(request):

    profile, _ = Profile.objects.get_or_create(user=request.user)

    limit = 3

    # 無料ユーザーだけ制限
    if not profile.is_premium and profile.ai_count >= limit:
        return redirect("pricing")

    answer = ""
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            answer = "質問を入力してください"
        else:
            try:
                if profile.is_premium:
                    max_tokens = 800
                else:
                    max_tokens = 200

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "あなたは副業コーチです"},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=max_tokens,
                    timeout=15
                )

                answer = response.choices[0].message.content

                # 無料ユーザーだけ回数加算
                if not profile.is_premium:
                    profile.ai_count += 1
                    profile.save()

            except Exception as e:
                answer = f"AIエラー: {e}"

    remaining = max(0, limit - profile.ai_count)

    return render(request, "snippets/ai_chat.html", {
        "answer": answer,
        "question": question,
        "remaining": remaining,
        "is_premium": profile.is_premium,
    })