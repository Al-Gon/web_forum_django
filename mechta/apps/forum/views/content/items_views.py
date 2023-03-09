# Core Django imports.
from django.views.generic import ListView
from mechta.apps.utils import DataMixin, set_read_topic
from django.db.models.functions import Rank, DenseRank
from django.db.models import Count, F, Window

# Forum application imports.
from forum.models import Message, Topic, Section


class ViewPage(DataMixin, ListView):
    model = Section
    context_object_name = 'page'
    template_name = 'forum/content/items/forum_content.html'

    def get_queryset(self):
        qw = self.model.objects. \
            annotate(num_messages=Window(expression=Count('topic__message__id'),
                                         partition_by=[F('id')])). \
            annotate(num_topics=Window(expression=DenseRank(),
                                       order_by=F('topic__id').desc(),
                                       partition_by=[F('id'), ])). \
            annotate(max_pub_date=Window(expression=Rank(),
                                         order_by=F('topic__message__pub_date').desc(),
                                         partition_by=[F('id'), ])).\
            values('id', 'title', 'description', 'icon',
                   'topic__id', 'topic__message__text',
                   'topic__message__pub_date',
                   'topic__message__user_id__username',
                   'topic__message__user_id__profile__land_plot__number',
                   'topic__message__user_id__profile__avatar__image_url',
                   'num_messages', 'num_topics').\
            order_by('-topic__message__pub_date')

        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        request=self.request,
                                        is_forum_page=True
                                        )
        return context


class SectionView(DataMixin, ListView):
    model = Topic
    context_object_name = 'page'
    template_name = 'forum/content/items/section_content.html'
    pk_url_kwarg = 'section_id'

    def get_queryset(self):
        qw = self.model.objects.\
            select_related('section_id').\
            filter(section_id=self.kwargs['section_id']).\
            annotate(num_messages=Count('message')). \
            order_by('pub_date'). \
            values('id', 'title', 'description', 'pub_date',
                   'section_id',
                   'section_id__title', 'section_id__description',
                   'num_messages')
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='section',
                                        is_forum_page=True,
                                        request=self.request,
                                        id=self.kwargs[self.pk_url_kwarg],
                                        values=['title', 'description', 'icon'])
        return context


class TopicView(DataMixin, ListView):
    model = Message
    context_object_name = 'page'
    template_name = 'forum/content/items/topic_content.html'
    pk_url_kwarg = 'topic_id'

    def get_queryset(self):
        qw = self.model.objects. \
            select_related('topic_id', 'user_id', 'user_id__profile'). \
            filter(topic_id=self.kwargs['topic_id']). \
            order_by('pub_date'). \
            values('id', 'text', 'pub_date',
                   'topic_id', 'user_id__username',
                   'user_id__profile__land_plot__number', 'user_id__profile__avatar__image_url'
                   )
        return qw

    def get_context_data(self, **kwargs):
        set_read_topic(self.request.user, self.kwargs[self.pk_url_kwarg])
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='topic',
                                        is_forum_page=True,
                                        request=self.request,
                                        id=self.kwargs[self.pk_url_kwarg],
                                        values=['title', 'description',
                                                'section_id__id', 'section_id__title', 'section_id__icon'])
        return context