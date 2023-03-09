# Core Django imports.
from django import forms
from django.contrib.auth.forms import UserCreationForm

# Forum application imports.
from forum.models import *


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