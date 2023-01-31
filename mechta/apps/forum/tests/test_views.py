from django.test import TestCase
from django.apps import apps
from django.urls import reverse
import random


NUM_USERS = 3
MAX_SECTIONS_ID = 7
NUM_TOPICS = 20
NUM_MESSAGES = 50


User = apps.get_model(app_label='auth', model_name='user')
Land_plot = apps.get_model(app_label='forum', model_name='LandPlot')
Profile = apps.get_model(app_label='forum', model_name='Profile')
Group = apps.get_model(app_label='auth', model_name='group')
Topic = apps.get_model(app_label='forum', model_name='Topic')
Message = apps.get_model(app_label='forum', model_name='Message')
Section = apps.get_model(app_label='forum', model_name='Section')


class ViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='forum_members')

        cls.test_settings = []
        usernames = ['Tester_' + str(i) for i in range(1, NUM_USERS + 1)]
        for i, username in enumerate(usernames, start=1):
            max_section_id_ = random.choice(list(range(1, MAX_SECTIONS_ID + 1)))
            num_topics_ = random.choice(list(range(1, NUM_TOPICS + 1)))
            num_messages_ = random.choice(list(range(1, NUM_MESSAGES + 1)))
            test_value_user__username_ = username
            test_value_user__first_name_ = username
            test_value_user__last_name_ = username
            test_value_phone_ = ''.join([str(random.choice(list(range(10)))) for _ in range(9)])
            test_value_num_topics_ = max_section_id_ * num_topics_
            test_value_num_messages_ = max_section_id_ * num_topics_ * num_messages_

            Land_plot.objects.create(number=str(i))
            land_plot_ = Land_plot.objects.get(id=i)

            item = {'user_id': i,
                    'max_section_id': max_section_id_,
                    'num_topics': num_topics_,
                    'num_messages': num_messages_,
                    'test_value_user__username': test_value_user__username_,
                    'test_value_user__first_name': test_value_user__first_name_,
                    'test_value_user__last_name': test_value_user__last_name_,
                    'test_value_phone': test_value_phone_,
                    'test_value_land_plot__number': land_plot_.number,
                    'test_value_num_topics': test_value_num_topics_,
                    'test_value_num_messages': test_value_num_messages_
                    }
            cls.test_settings.append(item)
            User.objects.create(username=test_value_user__username_,
                                email=username + '@example.com',
                                first_name=test_value_user__first_name_,
                                last_name=test_value_user__last_name_)
            user_ = User.objects.get(pk=i)

            Profile.objects.create(user=user_, land_plot=land_plot_, phone=test_value_phone_)

        max_section_id_settings = max(map(lambda x: x['max_section_id'], cls.test_settings))
        for i in range(1, max_section_id_settings + 1):
            Section.objects.create(title=f'раздел тест {i}', description=f'описание раздел тест {i}',
                                   icon=f'иконка тест {i}')
            section_ = Section.objects.get(pk=i)
            for item in cls.test_settings:
                user_ = User.objects.get(pk=item['user_id'])
                if i <= item['max_section_id']:
                    for j in range(1, item['num_topics'] + 1):
                        Topic.objects.create(user_id=user_, section_id=section_, title=f'тема тест {j}',
                                             description=f'описание раздел тест {i} тема тест {j}')
                        topic_ = Topic.objects.get(pk=j)
                        for k in range(1, item['num_messages'] + 1):
                            Message.objects.create(user_id=user_,
                                                   text=f'текст тема тест {j} сообщение тест {k}',
                                                   topic_id=topic_)


    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = '456@qwerty'
        self.phone = '123456789'
        self.land_plot_ = Land_plot.objects.get(pk='1')


    def tearDown(self):
        pass

    def test_userprofile_view_url(self):
        for item in self.test_settings:
            user_ = User.objects.get(pk=item['user_id'])
            user_slug = Profile.objects.filter(user=user_).values('slug')[0]['slug']
            self.client.force_login(user_)
            response = self.client.get(reverse('forum:user_profile', kwargs={'user_slug': user_slug}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template_name='forum/content/profile_content.html')


    def test_userprofile_view(self):
        for item in self.test_settings:
            user_ = User.objects.get(pk=item['user_id'])
            user_slug = Profile.objects.filter(user=user_).values('slug')[0]['slug']
            self.client.force_login(user_)
            response = self.client.get(reverse('forum:user_profile', kwargs={'user_slug': user_slug}))
            self.assertIsInstance(response.context_data, dict)
            page = response.context_data.get('page')
            self.assertEquals(page['user__username'], item['test_value_user__username'])
            self.assertEquals(page['user__first_name'], item['test_value_user__first_name'])
            self.assertEquals(page['user__last_name'], item['test_value_user__last_name'])
            # self.assertEquals(page['user__date_joined'], item['test_value_user__date_joined'])
            self.assertEquals(page['land_plot__number'], item['test_value_land_plot__number'])
            self.assertEquals(page['phone'], item['test_value_phone'])
            # self.assertEquals(page['last_visit'], item['test_value_last_visit'])
            # self.assertEquals(page['avatar__image_url'], item['test_value_avatar__image_url'])
            self.assertEquals(page['num_topics'], item['test_value_num_topics'])
            self.assertEquals(page['num_messages'], item['test_value_num_messages'])


    def test_register_page_url(self):
        response = self.client.get("/forum/register/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='forum/register_page.html')


    def test_register_form(self):
        post_data = {
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
            'phone': self.phone,
            'land_plot': self.land_plot_,
        }
        response = self.client.post(reverse('forum:register'), post_data, format='text/html')
        self.assertEqual(response.status_code, 302)
        users = User.objects.all()
        self.assertEqual(users.count(), NUM_USERS + 1)
        user_group = User.objects.get(pk=NUM_USERS + 1).groups.all()[0].name
        self.assertEqual(user_group, 'forum_members')