from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from snippets.models import Referral


def signup(request):

    ref = request.GET.get("ref")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username:
            return render(
                request,
                "snippets/signup.html",
                {"error": "ユーザー名を入力してください"}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "snippets/signup.html",
                {"error": "このユーザー名は既に使われています"}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 紹介カウント
        if ref:
            try:
                r = Referral.objects.get(code=ref)
                r.invited_count += 1
                r.save()
            except Referral.DoesNotExist:
                pass

        return redirect("login")

    return render(request, "snippets/signup.html")