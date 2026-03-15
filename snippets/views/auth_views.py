from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from snippets.forms import SignupForm
from snippets.models import Profile
from django.contrib.auth import login

def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile = Profile.objects.create(user=user)

        # 紹介コード取得
        ref = request.GET.get("ref")

        if ref:
            profile.referred_by = ref
            profile.save()

        return redirect("login")

    return render(request, "snippets/signup.html")


def signup(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("/")

    return render(request, "snippets/signup.html")
