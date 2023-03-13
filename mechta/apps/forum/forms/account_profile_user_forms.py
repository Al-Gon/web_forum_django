# Core Django imports.
from django import forms
from forum.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from mechta.utils.image_widget import ImageWidget
from email_validate import validate


def validate_email(value: str):
    """
    Returns forms.ValidationError if email address is not exist.
    :param value: email address
    :return: forms.ValidationError
    """

    if not validate(email_address=value,
                    check_format=True,
                    check_blacklist=True,
                    check_dns=True,
                    dns_timeout=10,
                    check_smtp=True,
                    smtp_debug=False):

        raise forms.ValidationError("Введите действительно существующий email адрес.")


class UserPasswordResetForm(SetPasswordForm):
    """
    Change password form.
    """

    new_password1 = forms.CharField(label='Новый пароль',
                                    max_length=100,
                                    required=True,
                                    widget=forms.PasswordInput(attrs={
                                                                      'class': 'form-control',
                                                                      'type': 'password',
                                                                      'id': 'user_password',
                                                                    }
                                                               )
                                    )

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
                                                                )
                                    )


class UserForgotPasswordForm(PasswordResetForm):
    """
    User forgot password, check via email form.
    """

    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))


class UserForm(UserCreationForm):
    """
    User registration form for signing up.
    """

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
    """
    User Profile registration form for signing up.
    """

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


class UserUpdateForm(forms.ModelForm):
    """
    User update form for update user data.
    """

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
    """
    User profile update form for update user profile data.
    """

    phone = forms.CharField(label='Телефон',
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ('phone', 'land_plot',)
        labels = {'land_plot': 'Номер участка'}
        widgets = {'land_plot': forms.Select(attrs={'class': 'form-select'})}


class AvatarUpdateForm(forms.ModelForm):
    """
    User avatar update form for update user avatar data.
    """

    image = forms.ImageField(label='Аватар',
                             required=False,
                             widget=ImageWidget())

    class Meta:
        model = Avatar
        fields = ('image',)


class LoginUserForm(AuthenticationForm):
    """
    User login form.
    """

    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))