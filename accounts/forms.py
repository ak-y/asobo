from django.forms import EmailField

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        # ↓ username と email の順番を入れ替え
        fields = ('email', 'username', 'password1', 'password2')
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'メールアドレス'}),
            'username': forms.TextInput(attrs={'placeholder': 'ユーザー名'}),
            'password1': forms.TextInput(attrs={'placeholder': 'パスワード'}),
            'password2': forms.TextInput(attrs={'placeholder': 'パスワード(再入力)'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'パスワード'})
        self.fields['password2'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'パスワード(再入力)'})

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        if commit:
            user.save()
        return user

