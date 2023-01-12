from django.test import TestCase, Client
from django.apps import apps
from django.urls import reverse
from django.contrib.auth.models import User

class ViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = apps.get_model(app_label='auth', model_name='user')
        land_plot = apps.get_model(app_label='forum', model_name='LandPlot')
        profile = apps.get_model(app_label='forum', model_name='Profile')
        topic = apps.get_model(app_label='forum', model_name='Topic')
        message = apps.get_model(app_label='forum', model_name='Message')
        section = apps.get_model(app_label='forum', model_name='Section')

        usernames = ['Tester_' + i for i in range(1, 5)]
        for i, username in enumerate(usernames, start=1):
            user.objects.create(username=username, email=username + '@example.com')
            user_ = user.objects.get(pk=i)
            land_plot.objects.create(number=str(i))
            land_plot_ = land_plot.objects.get(id=i)
            profile.objects.create(user=user_, land_plot=land_plot_, phone='12345660')


        section.objects.create(title='раздел тест 1', description='описание раздел тест 1',
                               icon='иконка тест 1')
        section_ = section.objects.get(id=1)
        topic.objects.create(user_id=user_, section_id=section_, title='тема тест 1',
                             description='описание тема тест 1')
        topic_ = topic.objects.get(id=1)
        message.objects.create(user_id=user_, topic_id=topic_, text='сообщение тест 1')

    def test_context_user_profile_views(self):
        user = apps.get_model(app_label='auth', model_name='user')
        user_ = user.objects.get(pk=1)
        profile = apps.get_model(app_label='forum', model_name='Profile')
        user_slug = profile.objects.filter(user=user_).values('slug')[0]['slug']
        c = Client()
        c.force_login(user_)

        response = c.get(reverse('forum:user_profile', kwargs={'user_slug': user_slug}))
        self.assertIsInstance(response.context_data, dict)
        page = response.context_data.get('page')
        self.assertEquals(page['num_messages'], 1)
        self.assertEquals(page['num_topics'], 1)