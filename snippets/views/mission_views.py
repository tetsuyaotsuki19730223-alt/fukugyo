from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from snippets.models import Profile, UserMission, Mission
from snippets.utils import calculate_level


@login_required
def mission(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    missions = Mission.objects.all().order_by("id")
    today = timezone.localdate()

    if not missions.exists():
        return render(request, "snippets/mission.html", {
            "mission": None,
            "profile": profile,
            "user_mission": None,
        })

    mission_index = today.toordinal() % missions.count()
    mission_obj = missions[mission_index]

    user_mission, _ = UserMission.objects.get_or_create(
        user=request.user,
        mission=mission_obj,
        assigned_date=today,
    )

    if request.method == "POST":
        if not user_mission.completed:
            user_mission.completed = True
            user_mission.save()

            profile.xp += mission_obj.xp
            profile.level = calculate_level(profile.xp)
            profile.save()

            messages.success(request, f"ミッション完了！ +{mission_obj.xp}XP 獲得しました。")
        else:
            messages.info(request, "このミッションはすでに完了しています。")

        return redirect("mission")

    return render(request, "snippets/mission.html", {
        "mission": mission_obj,
        "user_mission": user_mission,
        "profile": profile,
    })