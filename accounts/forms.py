from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"placeholder": "请输入用户名", "autocomplete": "username"}),
    )
    email = forms.EmailField(
        label="邮箱",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "选填", "autocomplete": "email"}),
    )
    password1 = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"placeholder": "至少 8 位", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(attrs={"placeholder": "再次输入密码", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"placeholder": "请输入用户名", "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"placeholder": "请输入密码", "autocomplete": "current-password"}),
    )
