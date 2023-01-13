from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from mechta.apps.image_widget import ImageWidget
from django.core.exceptions import ValidationError


class UserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

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
        widgets = {
                    'phone': forms.TextInput(attrs={'class': 'form-control'}),
                    'land_plot': forms.Select(attrs={'class': 'form-select'})
        }

    def add_user_pk(self, pk):
        self.instance.user_id = pk


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-control'}))
    # land_plot = forms.CharField(label='Участок', widget=forms.Select(attrs={'class': 'form-select'}))
    image = forms.ImageField(label='Аватар', required=False, widget=ImageWidget())

    class Meta:
        model = Profile
        fields = ('phone', 'land_plot', 'image')
        widgets = {
                    'land_plot': forms.Select(attrs={'class': 'form-select'})
        }



class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ReplyPostForm(forms.ModelForm):
    text = forms.CharField(label='Сообщение',
                           widget=forms.Textarea(attrs={'class': 'form-control','rows': 10, 'cols': 5}))

    class Meta(UserCreationForm):
        model = Message
        fields = ('text',)

    def add_user_id(self, id_):
        self.instance.user_id = id_

    def add_topic_id(self, id_):
        self.instance.topic_id = id_


class CreateTopicForm(forms.ModelForm):
    title = forms.CharField(label='Название темы',
                            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 10}))
    description = forms.CharField(label='Описание темы',
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 5}))

    class Meta(UserCreationForm):
        model = Topic
        fields = ('title', 'description',)

    def add_user_id(self, id_):
        self.instance.user_id = id_

    def add_section_id(self, id_):
        self.instance.section_id = id_