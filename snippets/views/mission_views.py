from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from snippets.models import Mission, UserMission, add_xp
import datetime


@login_required
def mission(request):

    profile = request.user.profile

    missions = Mission.objects.all()

    if not profile.is_premium:
        if user_mission.completed:
            return redirect("dashboard")

    if not missions.exists():
        return render(request, "snippets/mission.html")

    # 日替わり
    today = datetime.date.today().toordinal()
    mission = missions[today % missions.count()]

    user_mission, created = UserMission.objects.get_or_create(
        user=request.user,
        mission=mission
    )

    if profile.is_premium:
        add_xp(profile, mission.xp * 2)
    else:
        add_xp(profile, mission.xp)

    # 🔥 ここに書く！！！
    if request.method == "POST":

        if not user_mission.completed:
            user_mission.completed = True
            user_mission.save()

            # ✅ XP付与（ここ！）
            add_xp(profile, mission.xp)

        return redirect("mission")

    return render(request, "snippets/mission.html", {
        "mission": mission,
        "user_mission": user_mission
    })