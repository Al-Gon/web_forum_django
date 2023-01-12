from django.test import TestCase
from django.apps import apps


class ProfileTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = apps.get_model(app_label='auth', model_name='user')
        user.objects.create(username='Tester', email='tester@example.com', password='tester@1234')
        user_ = user.objects.get(pk=1)
        land_plot = apps.get_model(app_label='forum', model_name='LandPlot')
        land_plot.objects.create(number='100')
        land_plot_ = land_plot.objects.get(id=1)
        profile = apps.get_model(app_label='forum', model_name='Profile')
        profile.objects.create(user_id=user_.id, land_plot_id=land_plot_.id, phone='12345660')

    def test_slug(self):
        profile = apps.get_model(app_label='forum', model_name='Profile')
        profile_ = profile.objects.get(pk=1)
        self.assertEquals(profile_.slug, 'Tester-tester-example-com')