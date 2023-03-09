# Core Django imports.
from django.views.generic import CreateView
from mechta.apps.utils import DataMixin
from django.shortcuts import redirect

# Forum application imports.
from forum.forms.create_item_forms import *
from forum.models import Message, Topic


class CreateTopicView(DataMixin, CreateView):
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
        section_id = self.kwargs['section_id']
        section = Section.objects.get(id=section_id)
        user = self.request.user
        form.add_user_id(user)
        form.add_section_id(section)
        form.save()

        return redirect('forum:section', self.kwargs['section_id'])


class CreateMessage(DataMixin, CreateView):
    context_object_name = 'page'
    model = Message
    template_name = 'forum/content/create_item/reply_post.html'
    form_class = ReplyPostForm


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
        topic_id = self.kwargs['topic_id']
        topic = Topic.objects.get(id=topic_id)
        user = self.request.user
        form.add_user_id(user)
        form.add_topic_id(topic)
        form.save()

        return redirect('forum:topic', self.kwargs['section_id'], self.kwargs['topic_id'])