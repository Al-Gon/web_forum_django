# Core Django imports.
from django import forms
from forum.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from mechta.utils.image_widget import ImageWidget
from email_validate import validate


def validate_email(value):
    if not validate(email_address=value,
                    check_format=True,
                    check_blacklist=True,
                    check_dns=True,
                    dns_timeout=10,
                    check_smtp=True,
                    smtp_debug=False):

        raise forms.ValidationError("Введите действительно существующий email адрес.")


class UserPasswordResetForm(SetPasswordForm):
    """Change password form."""
    new_password1 = forms.CharField(label='Новый пароль',
                                    help_text="<ul class='errorlist text-muted'><li>Your password can 't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can 't be a commonly used password.</li> <li>Your password can 't be entirely numeric.<li></ul>",
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(attrs={
                                                                        'class': 'form-control',
                                                                        'type': 'password',
                                                                        'id': 'user_password',
                                    }))

    new_password2 = forms.CharField(label='Введите новый пароль повторно',
                                    help_text=False,
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(
                                                                attrs={
                                                                    'class': 'form-control',
                                                                    'type': 'password',
                                                                    'id': 'user_password',
                                                                        }
                                    ))


class UserForgotPasswordForm(PasswordResetForm):
    """User forgot password, check via email form."""
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))


class UserForm(UserCreationForm):
    username = forms.CharField(label='Логин',
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email',
                             required=True,
                             validators=[validate_email],
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль',
                                required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повтор пароля',
                                required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['land_plot'].empty_label = "Участок не выбран"

    class Meta(UserCreationForm):
        model = Profile
        fields = ('phone', 'land_plot')
        labels = {'land_plot': 'Номер участка'}
        widgets = {
                    'phone': forms.TextInput(attrs={'class': 'form-control'}),
                    'land_plot': forms.Select(attrs={'class': 'form-select'})
        }

    def add_user_pk(self, pk):
        self.instance.user_id = pk


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               disabled=True)
    first_name = forms.CharField(label='Имя',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия',
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email',
                             validators=[validate_email],
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(label='Телефон',
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ('phone', 'land_plot',)
        labels = {'land_plot': 'Номер участка'}
        widgets = {'land_plot': forms.Select(attrs={'class': 'form-select'})}


class AvatarUpdateForm(forms.ModelForm):
    image = forms.ImageField(label='Аватар',
                             required=False,
                             widget=ImageWidget())

    class Meta:
        model = Avatar
        fields = ('image',)


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))