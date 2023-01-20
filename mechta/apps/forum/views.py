from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from mechta.apps.utils import DataMixin, setup_session, delete_old_avatar_file, set_read_topic
from django.db.models import Count, F, Q, Window
from django.db.models.functions import Rank, DenseRank
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Subquery



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


class UserProfileUpdate(DataMixin, UpdateView):

    form_class = ProfileUpdateForm
    template_name = 'forum/profile_update_page.html'
    context_object_name = 'page'
    user_form = UserUpdateForm
    avatar_form = AvatarUpdateForm
    model = Profile
    slug_url_kwarg = 'user_slug'
    # success_url = reverse_lazy('forum:user_profile', kwargs={'user_slug': user_slug})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        context['user_form'] = self.user_form(instance=self.object.user)
        context['avatar_form'] = self.avatar_form(instance=self.object.avatar)
        return context

    def form_valid(self, form):
        user_form_ = self.user_form(self.request.POST, instance=self.object.user)
        if self.object.avatar is None:
            self.object.avatar = Avatar.objects.create()
        avatar_form_ = self.avatar_form(self.request.POST, self.request.FILES, instance=self.object.avatar)
        if user_form_.is_valid() and avatar_form_.is_valid():
            user_form_.save()
            delete_old_avatar_file(self.object.avatar)
            avatar_form_.save()

            form.save()
            return redirect('forum:user_profile', user_slug=self.kwargs[self.slug_url_kwarg])


class UserProfile(DataMixin, DetailView):
    context_object_name = 'page'
    model = Profile
    template_name = 'forum/content/profile_content.html'
    slug_url_kwarg = 'user_slug'

    def get_queryset(self):
        qw = self.model.objects.filter(slug=self.kwargs[self.slug_url_kwarg]).\
            annotate(num_messages=Count('user__message__id', distinct=True)).\
            annotate(num_topics=Count('user__topic__id', distinct=True)).\
            values('user__username', 'user__first_name',
                   'user__last_name', 'user__date_joined',
                   'land_plot', 'phone', 'last_visit', 'slug', 'avatar__image_url',
                   'num_messages', 'num_topics')
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        is_forum_page=True,
                                        )
        return context


class SearchResult(DataMixin, ListView):
    context_object_name = 'page'
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
        return qw

    def get_context_data(self, **kwargs):
        setup_session(self.request)
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('f_q')
        context = self.add_user_context(context=context,
                                        is_forum_page=True,
                                        request_path=self.request.path
                                        )
        return context


class CreateTopic(DataMixin, CreateView):
    context_object_name = 'page'
    model = Topic
    template_name = 'forum/create_topic.html'
    form_class = CreateTopicForm

    def get_context_data(self, **kwargs):
        setup_session(self.request)
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='section',
                                        is_forum_page=True,
                                        request_path=self.request.path,
                                        id=self.kwargs['section_id'],
                                        values=['id', 'title', 'description',
                                                'topic__title', 'topic__pub_date',
                                                'topic__user_id__username', 'topic__user_id__profile__land_plot',
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



class ReplyPost(DataMixin, CreateView):
    context_object_name = 'page'
    model = Message
    template_name = 'forum/reply_post.html'
    form_class = ReplyPostForm


    def get_context_data(self, **kwargs):
        setup_session(self.request)
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='topic',
                                        is_forum_page=True,
                                        request_path=self.request.path,
                                        id=self.kwargs['topic_id'],
                                        values=['id', 'title', 'description',
                                                'message__text', 'message__pub_date',
                                                'message__user_id__username',
                                                'message__user_id__profile__land_plot',
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


class ViewUnreadTopics(DataMixin, ListView):
    model = ForumReadTopic
    context_object_name = 'page'
    template_name = 'forum/content/unread_topics.html'

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
        setup_session(self.request)
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        is_forum_page=True,
                                        request_path=self.request.path,
                                        user=self.request.user
                                        )
        return context


class ViewTopic(DataMixin, ListView):
    model = Message
    context_object_name = 'page'
    template_name = 'forum/content/topic_content.html'
    pk_url_kwarg = 'topic_id'

    def get_queryset(self):

        qw = self.model.objects. \
            filter(topic_id=self.kwargs[self.pk_url_kwarg]). \
            select_related('topic_id', 'user_id', 'user_id__profile'). \
            order_by('pub_date'). \
            values('id', 'text', 'pub_date',
                   'topic_id', 'user_id__username',
                   'user_id__profile__land_plot', 'user_id__profile__avatar__image_url'
                   )
        return qw

    def get_context_data(self, **kwargs):
        setup_session(self.request, self.kwargs[self.pk_url_kwarg])
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='topic',
                                        is_forum_page=True,
                                        request_path=self.request.path,
                                        id=self.kwargs[self.pk_url_kwarg],
                                        values=['title', 'description',
                                                'section_id__id', 'section_id__title', 'section_id__icon'])
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
        setup_session(self.request)
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model='section',
                                        is_forum_page=True,
                                        request_path=self.request.path,
                                        id=self.kwargs[self.pk_url_kwarg],
                                        values=['title', 'description', 'icon'])
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
            values('id', 'title', 'description', 'icon',
                   'topic__id', 'topic__message__text',
                   'topic__message__pub_date',
                   'topic__message__user_id__username',
                   'topic__message__user_id__profile__land_plot',
                   'topic__message__user_id__profile__avatar__image_url',
                   'num_messages', 'num_topics').\
            order_by('-topic__message__pub_date')

        return qw

    def get_context_data(self, **kwargs):
        setup_session(self.request)
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        request_path=self.request.path,
                                        is_forum_page=True,
                                        user=self.request.user)
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