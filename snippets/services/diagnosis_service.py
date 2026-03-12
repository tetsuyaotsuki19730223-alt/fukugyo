def judge_result_type(data):

    if data["q1"] == "A":
        return "stable"

    if data["q1"] == "B":
        return "influence"

    if data["q1"] == "C":
        return "attack"

    return "build"