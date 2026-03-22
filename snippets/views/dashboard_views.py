from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from snippets.models import Profile, Mission, UserMission


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    xp = profile.xp
    level = profile.level
    streak = profile.streak

    current_level_start = (level - 1) * 100
    next_level_target = level * 100

    if next_level_target > current_level_start:
        progress = ((xp - current_level_start) / (next_level_target - current_level_start)) * 100
    else:
        progress = 0

    progress = max(0, min(progress, 100))
    next_level_xp = max(next_level_target - xp, 0)

    user_type = getattr(profile, "sidejob_type", "seller") or "seller"
    today = timezone.localdate()

    today_mission = None
    today_user_mission = None

    missions = Mission.objects.filter(mission_type=user_type).order_by("id")

    if missions.exists():
        mission_index = today.toordinal() % missions.count()
        today_mission = missions[mission_index]

        today_user_mission, _ = UserMission.objects.get_or_create(
            user=request.user,
            mission=today_mission,
            assigned_date=today,
        )

    messages_before = {
        "seller": "今日は『価値を言葉にする日』です。小さくても1つ提案してみましょう。",
        "build": "今日は『積み上げる日』です。完成より、少し前に進めることを大事にしましょう。",
        "influence": "今日は『伝える日』です。あなたの気づきを1つ発信してみましょう。",
        "stable": "今日は『続ける日』です。小さな一歩でも、積み重ねれば前進です。",
    }

    messages_after = {
        "seller": "今日のミッション達成です。次はAIチャットで売り方や提案の磨き方を相談してみましょう。",
        "build": "今日のミッション達成です。次はAIチャットで次に作るべきものを整理してみましょう。",
        "influence": "今日のミッション達成です。次はAIチャットで次の発信テーマを考えてみましょう。",
        "stable": "今日のミッション達成です。次はAIチャットで明日も続けやすい進め方を相談してみましょう。",
    }

    if today_user_mission and today_user_mission.completed:
        today_message = messages_after.get(
            user_type,
            "今日のミッション達成です。次の一歩も進めていきましょう。"
        )
    else:
        today_message = messages_before.get(
            user_type,
            "今日も小さく一歩進めていきましょう。"
        )

    return render(request, "snippets/dashboard.html", {
        "streak": streak,
        "level": level,
        "xp": xp,
        "progress": progress,
        "next_level_xp": next_level_xp,
        "is_premium": profile.is_premium,
        "today_mission": today_mission,
        "today_user_mission": today_user_mission,
        "today_message": today_message,
    })