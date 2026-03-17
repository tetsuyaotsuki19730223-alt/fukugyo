from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from snippets.models import Mission, UserMission, add_xp
import datetime


@login_required
def mission(request):

    profile = request.user.profile

    missions = Mission.objects.all()

    if not missions.exists():
        return render(request, "snippets/mission.html", {
            "mission": None
        })

    # ===================================
    # 🔥 ① missionを必ず先に作る
    # ===================================
    today = datetime.date.today().toordinal()
    mission = missions[today % missions.count()]

    # ===================================
    # 🔥 ② user_missionも先に作る（超重要）
    # ===================================
    user_mission, _ = UserMission.objects.get_or_create(
        user=request.user,
        mission=mission
    )

    # ===================================
    # 🔥 ③ POST処理（ここで使う）
    # ===================================
    if request.method == "POST":

        if not user_mission.completed:

            user_mission.completed = True
            user_mission.save()

            # XP付与
            if profile.is_premium:
                add_xp(profile, mission.xp * 2)
            else:
                add_xp(profile, mission.xp)

        return redirect("mission")

    return render(request, "snippets/mission.html", {
        "mission": mission,
        "user_mission": user_mission
    })