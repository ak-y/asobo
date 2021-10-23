from django.forms import PasswordInput

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from django.core.exceptions import ValidationError




class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        # ↓ username と email の順番を入れ替え
        fields = ('email', 'username', 'password1', 'password2')

        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'メールアドレス'}),
            'username': forms.TextInput(attrs={'placeholder': 'ユーザー名'}),
            # 'password1': forms.PasswordInput(attrs={'placeholder': 'パスワード'}),
            # 'password2': forms.PasswordInput(attrs={'placeholder': 'パスワード(再入力)'}),
        }
    def match_password(self):
        data = self.cleaned_data
        password = data.get("password")
        password2 = data.get("password2")
        if password != password2 :
            raise ValidationError("password must be same" )
        return data

    def double_email(self):
        email = self.cleaned_data.get("email")
        query_set = User.objects.filter(email=email)
        if email in query_set:
            return ValidationError("this e-mail is taken")
        return email

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'パスワード'})
        self.fields['password2'].widget = PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'パスワード(再入力)'})