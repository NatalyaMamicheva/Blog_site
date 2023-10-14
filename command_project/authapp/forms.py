import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите имя пользователя'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Введите адрес эл. почты'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Подтвердите пароль'}))
    avatar_link = forms.ImageField(widget=forms.FileInput(attrs={'class': 'custom-file-input'}), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean(self):
        cleaned_data = super(UserRegisterForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password1")
        email = cleaned_data.get("email")
        confirm_password = cleaned_data.get("password2")
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Никнейм уже занят."
            )
        elif len(username) < 3 or len(username) > 15:
            raise forms.ValidationError(
                "Никнейм должен быть больше (от 3 до 15 символов)."
            )
        elif User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Данный email уже зарегистрирован на сайте."
            )
        elif password != confirm_password:
            raise forms.ValidationError(
                "Пароли не совпадают."
            )
        elif len(password) <= 6:
            raise forms.ValidationError(
                "Пароль должен содержать не менее 6 символов."
            )
        elif r'\w' not in password.split() and re.match(pattern, password) is None and (
                password.isupper() or password.islower()):
            raise forms.ValidationError(
                "Пароль должен содержать строчные латинские буквы в верхнем и нижнем регистрах."
            )
        

class UserProfileForm(UserChangeForm):
    username = forms.CharField(widget=forms.TextInput())
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    avatar_link = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'avatar_link', 'first_name', 'last_name', 'user_about')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4', 'placeholder': 'Введите имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4', 'placeholder': 'Введите пароль'}))

    class Meta:
        model = User
        fields = ('username', 'password')
