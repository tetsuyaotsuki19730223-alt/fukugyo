from django import forms


class SignupForm(forms.Form):

    username = forms.CharField()

    password1 = forms.CharField(
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput
    )