from django.shortcuts import render
from django.core.mail import send_mail
from snippets.forms import ContactForm


def privacy(request):
    return render(request, "snippets/privacy.html")


def terms(request):
    return render(request, "snippets/terms.html")


def legal(request):
    return render(request, "snippets/legal.html")


def contact(request):

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            message = form.cleaned_data["message"]

            send_mail(
                "お問い合わせ",
                message,
                email,
                ["tetsuyaotsuki19730223@gmail.com"]
            )

            return render(
                request,
                "snippets/contact_success.html"
            )

    else:

        form = ContactForm()

    return render(
        request,
        "snippets/contact.html",
        {"form": form}
    )
