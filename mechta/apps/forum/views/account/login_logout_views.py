# Core Django imports.
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

# Forum application imports.
from mechta.apps.utils import DataMixin
from forum.forms.account_profile_user_forms import *


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'forum/account/registration/../../../../templates/forum/account/login_logout/login_page.html'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        return context

    def get_success_url(self):
        return reverse_lazy('forum:home')


def logout_user(request):
    logout(request)
    return redirect('forum:login')