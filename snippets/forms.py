from django import forms


class SignupForm(forms.Form):

    username = forms.CharField(max_length=150)

    email = forms.EmailField()

    password = forms.CharField(widget=forms.PasswordInput)    

class ContactForm(forms.Form):

    email = forms.EmailField(label="メール")

    message = forms.CharField(
        label="お問い合わせ内容",
        widget=forms.Textarea
    )
