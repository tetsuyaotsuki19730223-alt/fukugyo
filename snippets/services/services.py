def judge_result_type(cleaned: dict) -> str:
    """
    stable / influence / attack / build を返す
    まずはルールベースで十分。後で改善できる。
    """
    score = {"stable": 0, "influence": 0, "attack": 0, "build": 0}

    # 得意（最重要）
    s = cleaned["q3_strength"]
    if s == "make":
        score["stable"] += 2
        score["build"] += 2
    elif s == "post":
        score["influence"] += 4
    elif s == "resell":
        score["attack"] += 4
    elif s == "analyze":
        score["build"] += 3
        score["stable"] += 1

    # 時間
    t = cleaned["q2_time"]
    if t in ("lt30", "h1"):
        score["stable"] += 1
        score["influence"] += 1
    else:
        score["build"] += 1
        score["attack"] += 1

    # リスク
    r = cleaned["q4_risk"]
    if r == "low":
        score["stable"] += 2
    elif r in ("high", "very"):
        score["attack"] += 2
        score["build"] += 1

    # 目標
    g = cleaned["q5_goal"]
    if g in ("1", "5"):
        score["stable"] += 1
        score["influence"] += 1
    elif g == "10":
        score["stable"] += 1
        score["attack"] += 1
        score["build"] += 1
    elif g == "indep":
        score["build"] += 2
        score["influence"] += 1

    # 最大スコアのキーを返す
    return max(score, key=score.get)