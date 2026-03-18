from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from snippets.models import Profile
from snippets.utils import calculate_level


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    today = timezone.now().date()

    if profile.last_login_date != today:
        yesterday = today - timezone.timedelta(days=1)

        if not profile.last_login_date:
            profile.streak = 1
        elif profile.last_login_date == yesterday:
            profile.streak += 1
        else:
            if profile.is_premium and profile.streak_freeze:
                pass
            else:
                profile.streak = 1

        bonus = 10
        if profile.is_premium:
            bonus = 30

        profile.xp = (profile.xp or 0) + bonus
        profile.last_login_date = today

    new_level = calculate_level(profile.xp or 0)
    if new_level != profile.level:
        profile.level = new_level

    profile.save()

    xp = profile.xp or 0
    progress = xp % 100
    next_level_xp = profile.level * 100 - xp

    return render(request, "snippets/dashboard.html", {
        "progress": progress,
        "streak": profile.streak,
        "xp": xp,
        "level": profile.level,
        "next_level_xp": next_level_xp,
        "is_premium": profile.is_premium,
    })