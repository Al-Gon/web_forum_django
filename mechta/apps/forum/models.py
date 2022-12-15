from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class LandPlot(models.Model):
    NUMBERS = list(map(lambda x: (str(x), str(x)), range(1, 300)))
    number = models.CharField('номер участка', choices=NUMBERS, max_length=3)

    def __str__(self):
        return self.number

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    land_plot = models.ForeignKey(LandPlot, on_delete=models.CASCADE)
    phone = models.CharField('телефон', max_length=20, blank=True)


class Section(models.Model):
    title = models.TextField('название раздела')
    description = models.TextField('описание раздела')
    pub_date = models.DateField('дата создания', default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        host = 'http://127.0.0.1:8000/'
        return host + 'forum/' + str(self.pk) + '/'


class Topic(models.Model):
    title = models.TextField('название темы')
    description = models.TextField('описание темы')
    pub_date = models.DateField('дата создания', default=timezone.now)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        host = 'http://127.0.0.1:8000/'
        return host + 'forum/' + str(self.section_id) + '/' + str(self.pk) + '/'



class Message(models.Model):
    text = models.TextField('сообщение')
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE)
    pub_date = models.DateField('дата публикации', default=timezone.now)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        get_latest_by = 'pub_date'

    def __str__(self):
        return self.text