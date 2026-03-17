from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.models import Profile
from django.utils import timezone


def home(request):
    context = {
        "streak": 5,
        "xp": 120,
        "level": 2,
        "mission": "副業リサーチを10分する"
    }
    return render(request, "snippets/dashboard.html")

def landing(request):
    return render(request, "snippets/landing.html")


@login_required
def dashboard(request):

    profile = request.user.profile
    today = timezone.now().date()

    # ===================================
    # 🔥 初回 or 日付変わったときだけ処理
    # ===================================
    if profile.last_login_date != today:

        yesterday = today - timezone.timedelta(days=1)

        # 🔥 streak処理
        if not profile.last_login_date:
            profile.streak = 1

        elif profile.last_login_date == yesterday:
            profile.streak += 1

        else:
            # 🔥 プレミアムなら守る
            if profile.is_premium and profile.streak_freeze:
                pass
            else:
                profile.streak = 1

        # ===================================
        # 🔥 ログインボーナス（1日1回）
        # ===================================
        bonus = 10
        if profile.is_premium:
            bonus = 30

        profile.xp += bonus

        # 日付更新
        profile.last_login_date = today
        profile.save()

    # ===================================
    # 🔥 XPバー
    # ===================================
    xp = profile.xp or 0
    progress = xp % 100

    return render(request, "snippets/dashboard.html", {
        "progress": progress,
        "streak": profile.streak
    })

def to_int(value):
    try:
        return int(value)
    except:
        return 0
    
def some_view(request):
    value = to_int(request.POST.get("xxx"))