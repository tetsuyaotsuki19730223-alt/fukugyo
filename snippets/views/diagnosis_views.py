from django.shortcuts import render, redirect


def diagnosis(request):
    return render(request, "snippets/diagnosis.html")

def result(request):

    result = {
        "type": "Influencer型",
        "description": "SNS発信で収益化するタイプです"
    }

    return render(
        request,
        "snippets/result.html",
        {"result": result}
    )

def type_diagnosis(request):

    if request.method == "POST":

        q1 = request.POST.get("q1")

        if q1 == "A":

            result = "creator"

        elif q1 == "B":

            result = "seller"

        elif q1 == "C":

            result = "influencer"

        else:

            result = "stable"

        return redirect(f"/ai-roadmap/?type={result}")

    return render(request, "snippets/type_diagnosis.html")


def history(request):
    return render(request, "snippets/history.html")

def ai_report(request):
    return render(request, "snippets/ai_report.html")


def roadmap_result(request):
    return render(request, "snippets/roadmap_result.html")