from django.shortcuts import render


def blog_ai_sidejob(request):

    return render(
        request,
        "snippets/blog_ai_sidejob.html"
    )