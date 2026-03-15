from django import forms


from django import forms


class SignupForm(forms.Form):

    username = forms.CharField()

    password1 = forms.CharField(
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 != p2:
            raise forms.ValidationError("パスワードが一致しません")

        return cleaned_data
    

class ContactForm(forms.Form):

    email = forms.EmailField(label="メール")

    message = forms.CharField(
        label="お問い合わせ内容",
        widget=forms.Textarea
    )
