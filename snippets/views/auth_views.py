from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect


def signup(request):

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

        # ここが重要
        login(request, user)

        return redirect("dashboard")

    return render(request, "snippets/signup.html")