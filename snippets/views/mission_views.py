from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from snippets.models import Mission, UserMission, add_xp
import datetime


@login_required
def mission(request):

    profile = request.user.profile

    missions = Mission.objects.all()

    # ❗ ミッションがない場合
    if not missions.exists():
        return render(request, "snippets/mission.html", {
            "mission": None
        })

    # ✅ ここで必ず作る（重要）
    today = datetime.date.today().toordinal()
    mission = missions[today % missions.count()]

    # ✅ ここも必ず mission の後
    user_mission, _ = UserMission.objects.get_or_create(
        user=request.user,
        mission=mission
    )

    # ✅ POST処理
    if request.method == "POST":

        if not user_mission.completed:
            user_mission.completed = True
            user_mission.save()

            add_xp(profile, mission.xp)

        return redirect("mission")

    return render(request, "snippets/mission.html", {
        "mission": mission,
        "user_mission": user_mission
    })