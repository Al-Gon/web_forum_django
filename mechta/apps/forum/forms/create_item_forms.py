# Core Django imports.
from django import forms
from django.contrib.auth.forms import UserCreationForm

# Forum application imports.
from forum.models import *


class CreateTopicForm(forms.ModelForm):
    """
    Form for creating a new topic.
    """

    title = forms.CharField(label='Название темы',
                            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 10}))
    description = forms.CharField(label='Описание темы',
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 5}))

    class Meta(UserCreationForm):
        model = Topic
        fields = ('title', 'description',)


class CreateMessageForm(forms.ModelForm):
    """
    Form for creating a new message.
    """

    text = forms.CharField(label='Сообщение',
                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'cols': 5}))

    class Meta(UserCreationForm):
        model = Message
        fields = ('text',)