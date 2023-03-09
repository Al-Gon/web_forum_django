# Core Django imports.
from django.contrib.auth.models import User
from django.db.models import Q, Case, Value, When
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.views.generic import ListView
from mechta.apps.utils import DataMixin, set_read_topic
from django.db.models import Count, F
from django.db.models import Subquery

# Forum application imports.
from forum.models import ForumReadTopic, Topic, Section


@csrf_exempt
def topic_handler(request):
    if request.is_ajax():
        topic_id = request.POST.get('topic_id')
        checked = request.POST.get('checked')
        if checked == 'true':
            set_read_topic(user=request.user, topic_id=topic_id)

            return JsonResponse({"topic_id": str(topic_id)}, status=200)
        else:
            return JsonResponse({}, status=200)


class UnreadTopicView(DataMixin, ListView):
    model = ForumReadTopic
    context_object_name = 'page'
    template_name = 'forum/content/stuff/unread_topics.html'

    def get_queryset(self):
        read_topics = self.model.objects.filter(user=self.request.user)
        qw1 = Topic.objects.exclude(id__in=Subquery(read_topics.values('topic'))).\
            annotate(num_messages=Count('message')).\
            values('num_messages', 'id', 'title', 'description', 'section_id')

        qw2 = self.model.objects.\
            filter(user=self.request.user, topic__message__pub_date__gt=F('last_view')).\
            annotate(num_messages=Count('topic__message')).\
            values('num_messages', 'topic_id', 'topic__title', 'topic__description', 'topic__section_id')

        return qw2.union(qw1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        is_forum_page=True,
                                        request=self.request
                                        )
        return context


class SearchResult(DataMixin, ListView):
    context_object_name = 'page'
    model = Section
    template_name = 'forum/content/stuff/forum_search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('f_q')
        qw = self.model.objects. \
            filter(Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(topic__title__icontains=query) |
                   Q(topic__description__icontains=query) |
                   Q(topic__message__text__icontains=query)). \
            values('id', 'title', 'description',
                   'topic__id', 'topic__title', 'topic__description',
                   'topic__message__id', 'topic__message__text')
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('f_q')
        context = self.add_user_context(context=context,
                                        is_forum_page=True,
                                        request=self.request
                                        )
        return context


class ViewMembers(DataMixin, ListView):
    model = User
    template_name = 'forum/content/stuff/members_page.html'
    context_object_name = 'page'

    def get_queryset(self):
        gr = Group.objects.prefetch_related('user_set').get(name='forum_members')
        members = gr.user_set.all().values_list('id', flat=True)

        qw = self.model.objects.\
            select_related('message', 'profile', 'profile__land_plot', 'profile__avatar'). \
            annotate(is_member=Case(When(id__in=members, then=Value('пользователь')), default=Value('администратор'))).\
            annotate(num_messages=Count('message__id')). \
            order_by('date_joined'). \
            values('username', 'profile__last_visit', 'profile__slug',
                   'profile__land_plot__number', 'profile__avatar__image_url',
                   'num_messages', 'is_member')
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        request=self.request,
                                        is_forum_page=True
                                        )
        return context