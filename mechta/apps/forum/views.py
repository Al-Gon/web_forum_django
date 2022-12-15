from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from mechta.apps.utils import DataMixin
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.db.models.functions import Rank, DenseRank
from .forms import *
from .models import Topic, Section, Message, Profile
from django.contrib.auth.models import User
from django.db.models import FilteredRelation, Q
from django.db.models import Avg, F, Window

# class TestView(DataMixin, ListView):
#     model = Section
#     template_name = 'forum/shlak/test.html'
#     context_object_name = 'page'
#
#     def get_queryset(self):
#         qw = Section.objects.all().values('id', 'title', 'description')
#         return qw
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context = self.add_user_context(context=context,
#                                         is_forum_page=True)
#         return context
#
#
# def test(request):
#     qw = Section.objects.all().values('id', 'title', 'description')
#     context = {'page': qw}
#     return render(request, 'forum/shlak/test.html', context=context)


class SearchResult(DataMixin, ListView):
    context_object_name = 'page'
    # model = Message
    model = Section
    template_name = 'forum/content/forum_search_results.html'

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

        # qw = self.model.objects. \
        #     values('text', 'id',
        #            'topic_id__id', 'topic_id__title', 'topic_id__description',
        #            'topic_id__section_id__id', 'topic_id__section_id__title', 'topic_id__section_id__description'). \
        #     filter(Q(text__icontains=query) |
        #            Q(topic_id__title__icontains=query) |
        #            Q(topic_id__description__icontains=query) |
        #            Q(topic_id__section_id__title__icontains=query) |
        #            Q(topic_id__section_id__description__icontains=query))
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('f_q')
        context = self.add_user_context(context=context,
                                        is_forum_page=True
                                        )
        return context


class CreateTopic(DataMixin, CreateView):
    model = Topic
    template_name = 'forum/create_topic.html'
    form_class = CreateTopicForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='section',
                                        is_forum_page=True,
                                        id=self.kwargs['section_id'],
                                        values=['title', 'description']
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



class ReplyPost(DataMixin, CreateView):
    context_object_name = 'page'
    model = Message
    template_name = 'forum/reply_post.html'
    form_class = ReplyPostForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='topic',
                                        is_forum_page=True,
                                        id=self.kwargs['topic_id'],
                                        values=['id', 'title', 'description',
                                                'message__text', 'message__pub_date',
                                                'message__user_id__username',
                                                'message__user_id__profile__land_plot',
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


class ViewTopic(DataMixin, ListView):
    model = Message
    context_object_name = 'page'
    template_name = 'forum/content/topic_content.html'
    pk_url_kwarg = 'topic_id'

    def get_queryset(self):
        qw = self.model.objects. \
            filter(topic_id=self.kwargs[self.pk_url_kwarg]). \
            select_related('topic_id', 'user_id', 'user_id__profile'). \
            order_by('pub_date').\
            values('id', 'text', 'pub_date',
                   'topic_id', 'user_id__username',
                   'user_id__profile__land_plot'
                   )
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='topic',
                                        is_forum_page=True,
                                        id=self.kwargs[self.pk_url_kwarg],
                                        values=['title', 'description',
                                                'section_id__id', 'section_id__title'])
        return context


class ViewSection(DataMixin, ListView):
    model = Topic
    context_object_name = 'page'
    template_name = 'forum/content/section_content.html'
    pk_url_kwarg = 'section_id'

    def get_queryset(self):
        qw = self.model.objects.\
            filter(section_id=self.kwargs[self.pk_url_kwarg]).\
            select_related('section_id').\
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
                                        id=self.kwargs[self.pk_url_kwarg],
                                        values=['title', 'description'])
        return context


class ViewPage(DataMixin, ListView):
    model = Section
    context_object_name = 'page'
    template_name = 'forum/content/forum_content.html'


    def get_queryset(self):
        # qw = self.model.objects.\
        #     annotate(num_topics=Count('topic__id', distinct=True)).\
        #     annotate(num_messages=Count('topic__message__id', distinct=True)).\
        #     values('id', 'title', 'description', 'num_topics', 'num_messages',
        #            'topic__message__pub_date', 'topic__message__text')
        #     # annotate(latest_message=FilteredRelation('topic__message__pub_date',
        #     #                                          condition=Q(topic__message__pub_date=Max('topic__message__pub_date')))).\
        #     # values('topic__message__pub_date', 'topic__message__text', 'latest_message')

        qw = self.model.objects. \
            annotate(num_messages=Window(expression=Count('topic__message__id'),
                                         partition_by=[F('id')])). \
            annotate(num_topics=Window(expression=DenseRank(),
                                       order_by=F('topic__id').desc(),
                                       partition_by=[F('id'), ])). \
            annotate(max_pub_date=Window(expression=Rank(),
                                         order_by=F('topic__message__pub_date').desc(),
                                         partition_by=[F('id'), ])).\
            values('id', 'title', 'description',
                   'topic__id', 'topic__message__text',
                   'topic__message__user_id__username',
                   'topic__message__user_id__profile__land_plot',
                   'num_messages', 'num_topics').\
            order_by('-topic__message__pub_date')

        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        is_forum_page=True)
        return context


class RegisterUser(DataMixin, CreateView):
    form_class = UserForm
    template_name = 'forum/register_page.html'
    success_url = reverse_lazy('login')
    context_object_name = 'page'
    pro_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        context['pro_form'] = self.pro_form
        return context

    def form_valid(self, form):
        pro_form_ = self.pro_form(self.request.POST)
        if pro_form_.is_valid():
            user = form.save()
            pro_form_.add_user_pk(user.pk)
            pro_form_.save()
            login(self.request, user)
            return redirect('forum:page')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'forum/login_page.html'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context

    def get_success_url(self):
        return reverse_lazy('forum:page')


def logout_user(request):
    logout(request)
    return redirect('forum:login')