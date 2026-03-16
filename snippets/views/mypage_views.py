from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def mypage(request):

    profile = request.user.profile

    ref_link = f"/signup/?ref={profile.referral_code}"

    context = {
        "user": request.user,
        "profile": profile,
        "ref_link": ref_link
    }

    return render(request, "snippets/mypage.html", context)

def my_page(request):
    return render(request, "snippets/my_page.html")