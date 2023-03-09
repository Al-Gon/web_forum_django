# Core Django imports.
from django.shortcuts import redirect, render
from django.views.generic import DetailView, View
from django.db.models import Count

# Forum application imports.
from forum.forms.account_profile_user_forms import *
from forum.models import Profile, Avatar
from mechta.apps.utils import DataMixin


class UserProfile(DataMixin, DetailView):
    """
    Displays user profile details
    """
    context_object_name = 'page'
    model = Profile
    template_name = 'forum/content/profile_content.html'
    slug_url_kwarg = 'user_slug'

    def get_queryset(self):
        qw = self.model.objects.select_related('user', 'land_plot', 'avatar').\
            annotate(num_messages=Count('user__message__id', distinct=True)).\
            annotate(num_topics=Count('user__topic__id', distinct=True)). \
            values('user__username', 'user__first_name',
                   'user__last_name', 'user__date_joined',
                   'land_plot__number', 'phone', 'last_visit', 'slug', 'avatar__image_url',
                   'num_messages', 'num_topics')
        return qw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context


class UserProfileUpdate(DataMixin, View):
    """
    Updates user profile details
    """
    template_name = 'forum/user_profile/profile_update_page.html'
    context_object = {}

    def get(self, request, **kwargs):
        user_form = UserUpdateForm(instance=self.request.user)
        profile_form = ProfileUpdateForm(instance=self.request.user.profile)
        avatar_form = AvatarUpdateForm(instance=self.request.user.profile.avatar)

        self.context_object = self.add_user_context(context=self.context_object)
        self.context_object['user_form'] = user_form
        self.context_object['profile_form'] = profile_form
        self.context_object['avatar_form'] = avatar_form

        return render(request, self.template_name, self.context_object)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_form = UserUpdateForm(data=request.POST,
                                   instance=user)
        profile_form = ProfileUpdateForm(data=request.POST,
                                         instance=user.profile)

        if user.profile.avatar is None:
            user.profile.avatar = Avatar.objects.create()

        avatar_form = AvatarUpdateForm(data=request.POST,
                                       files=request.FILES,
                                       instance=user.profile.avatar)

        if user_form.is_valid() and avatar_form.is_valid() and profile_form.is_valid():
            user_form.save()
            avatar_form.save()
            profile_form.save()

            return redirect('forum:user_profile', user_slug=user.profile.slug)

        user_form = UserUpdateForm(data=request.POST,
                                   instance=user)
        profile_form = ProfileUpdateForm(data=request.POST,
                                         instance=user.profile)
        avatar_form = AvatarUpdateForm(data=request.POST,
                                       instance=user.profile.avatar)

        self.context_object = self.add_user_context(context=self.context_object)
        self.context_object['user_form'] = user_form
        self.context_object['profile_form'] = profile_form
        self.context_object['avatar_form'] = avatar_form

        return render(request, self.template_name, self.context_object)