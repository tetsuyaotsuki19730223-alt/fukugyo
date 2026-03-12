def complete_mission(profile, mission):

    profile.xp += mission.xp_reward

    profile.level = calculate_level(profile.xp)

    profile.save()