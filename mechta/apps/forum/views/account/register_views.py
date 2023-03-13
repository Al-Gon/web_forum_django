# Core Django imports.
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, TemplateView, View
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import render
from django.core.mail import EmailMessage

# Forum application imports.
from mechta.apps.utils import DataMixin
from forum.forms.account_profile_user_forms import *
from forum.models import Profile
from mechta.tokens import account_activation_token


class RegisterUser(DataMixin, View):
    """
    Registration of a new user.
    """
    context_object = {}
    template_name = 'forum/account/registration/register_page.html'

    def get(self, request, **kwargs):
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)

        self.context_object = self.add_user_context(context=self.context_object)
        self.context_object['user_form'] = user_form
        self.context_object['profile_form'] = profile_form

        return render(request, self.template_name, self.context_object)

    def post(self, request, *args, **kwargs):
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()
            profile_form.instance.user_id = user.pk
            profile_form.save()
            forum_members = Group.objects.get(name='forum_members')
            user.groups.add(forum_members)
            user.save()

            site = get_current_site(self.request)
            mail_subject = f'Активация аккаунта на форуме сайта {site}.'
            to_email = user.email
            message = render_to_string('forum/account/registration/activation_email.html', {
                'username': user.username,
                'protocol': 'http',
                'domain': site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            email = EmailMessage(mail_subject, message, to=[to_email])
            email.content_subtype = 'html'
            email.send()
            return redirect(reverse_lazy('forum:activation_confirm',
                                         kwargs={'user_slug': user.profile.slug}))

        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)

        self.context_object = self.add_user_context(context=self.context_object)
        self.context_object['user_form'] = user_form
        self.context_object['profile_form'] = profile_form

        return render(request, self.template_name, self.context_object)


class ActivationConfirm(DataMixin, DetailView):
    context_object_name = 'page'
    model = Profile
    template_name = 'forum/account/registration/activation_confirm_page.html'
    slug_url_kwarg = 'user_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context


class ActivateUser(DataMixin, TemplateView):
    context_object_name = 'page'
    template_name = 'forum/account/registration/activation_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        token = self.kwargs['token']
        uidb64 = self.kwargs['uidb64']
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            profile = Profile.objects.get(user=user)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            profile.email_confirmed = True
            profile.save()
            login(self.request, user)
            context['message'] = '<p>Ваш аккаунт был подтверждён успешно.</p>' \
                                 '<p>Вы будите перенаправлены на главную страницу форума.</p>'
        else:
            context['message'] = '<p>Ссылка для активации аккаунта устарела.</p><p>Пройдите регистрацию заново!</p>'
        return context


class PasswordReset(DataMixin, PasswordResetView):
    context_object_name = 'page'
    template_name = 'forum/account/registration/password_reset_page.html'
    form_class = UserForgotPasswordForm
    email_template_name = 'forum/account/registration/password_reset_email.html'
    html_email_template_name = 'forum/account/registration/password_reset_email.html'
    success_url = reverse_lazy('forum:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context


class PasswordResetDone(DataMixin, PasswordResetDoneView):
    context_object_name = 'page'
    template_name = 'forum/account/registration/password_reset_done_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context


class PasswordResetConfirm(DataMixin, PasswordResetConfirmView):
    context_object_name = 'page'
    template_name = 'forum/account/registration/password_reset_confirm_page.html'
    form_class = UserPasswordResetForm
    success_url = reverse_lazy("forum:password_reset_complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context


class PasswordResetComplete(DataMixin, PasswordResetCompleteView):
    context_object_name = 'page'
    template_name = 'forum/account/registration/password_reset_complete_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context