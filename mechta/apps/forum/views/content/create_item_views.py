# Core Django imports.
from django.views.generic import CreateView
from mechta.apps.utils import DataMixin
from django.shortcuts import redirect, get_object_or_404

# Forum application imports.
from forum.forms.create_item_forms import *
from forum.models import Message, Topic


class CreateTopicView(DataMixin, CreateView):
    """
    Display page for creating a new topic.
    """

    context_object_name = 'page'
    model = Topic
    template_name = 'forum/content/create_item/create_topic.html'
    form_class = CreateTopicForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='section',
                                        is_forum_page=True,
                                        request=self.request,
                                        id=self.kwargs['section_id'],
                                        values=['id', 'title', 'description',
                                                'topic__title', 'topic__pub_date',
                                                'topic__user_id__username',
                                                'topic__user_id__profile__land_plot__number',
                                                'topic__user_id__profile__avatar__image_url'],
                                        order_by=['-topic__pub_date']
                                        )
        return context

    def form_valid(self, form):
        topic = form.save(commit=False)
        topic.section_id = get_object_or_404(Section, pk=self.kwargs.get('section_id'))
        topic.user_id = self.request.user
        topic.save()

        return redirect('forum:section', self.kwargs['section_id'])


class CreateMessage(DataMixin, CreateView):
    """
    Display page for creating a new message.
    """

    context_object_name = 'page'
    model = Message
    template_name = 'forum/content/create_item/create_message.html'
    form_class = CreateMessageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='topic',
                                        is_forum_page=True,
                                        request=self.request,
                                        id=self.kwargs['topic_id'],
                                        values=['id', 'title', 'description',
                                                'message__text', 'message__pub_date',
                                                'message__user_id__username',
                                                'message__user_id__profile__land_plot__number',
                                                'message__user_id__profile__avatar__image_url',
                                                'section_id__id', 'section_id__title'],
                                        order_by=['-message__pub_date']
                                        )

        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.topic_id = get_object_or_404(Topic, pk=self.kwargs.get('topic_id'))
        message.user_id = self.request.user
        message.save()

        return redirect('forum:topic', self.kwargs['section_id'], self.kwargs['topic_id'])