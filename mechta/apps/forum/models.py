from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from functools import reduce
from mechta.utils.ascii_filesystem_storage import ASCIIFileSystemStorage


class LandPlot(models.Model):
    NUMBERS = list(map(lambda x: (str(x), str(x)), range(1, 300)))
    number = models.CharField('номер участка', choices=NUMBERS, max_length=3, unique=True)

    def __str__(self):
        return self.number

class Avatar(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to="images/profile/", storage=ASCIIFileSystemStorage())
    image_url = models.URLField(null=True, blank=True)

    def get_image_url(self):
        try:
            if self.image.name:
                if self.image.field.upload_to not in self.image.name:
                    url = self.image.storage.get_pre_name(self.image.field.upload_to + self.image.name)
                else:
                    url = self.image_url
            else:
                raise ValueError
        except ValueError:
            url = ''
        return url

    def save(self, *args, **kwargs):
        self.image_url = self.get_image_url()
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    slug = models.SlugField('url', max_length=255, db_index=True, unique=True)
    land_plot = models.ForeignKey(LandPlot, on_delete=models.CASCADE, null=True)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    phone = models.CharField('телефон', max_length=20, blank=True)
    last_visit = models.DateTimeField('последнее посещение', default=timezone.now)
    email_confirmed = models.BooleanField(default=False)
    reset_password = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        self.slug = self.user.username + '-' + \
                    reduce(lambda x, y: x + '-' if y in ['@', '.'] else x + y, list(self.user.email))
        super().save(*args, **kwargs)



class Section(models.Model):
    title = models.TextField('название раздела')
    description = models.TextField('описание раздела')
    icon = models.CharField('иконка', max_length=50, default="", blank=True)
    pub_date = models.DateField('дата создания', default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        host = 'http://127.0.0.1:8000/'
        return host + 'forum/' + str(self.pk) + '/'


class Topic(models.Model):
    title = models.TextField('название темы')
    description = models.TextField('описание темы')
    pub_date = models.DateTimeField('дата создания', default=timezone.now)
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
    pub_date = models.DateTimeField('дата публикации', default=timezone.now)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        get_latest_by = 'pub_date'

    def __str__(self):
        return self.text


class ForumSession(models.Model):
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE)
    expire_date = models.DateTimeField('Время жизни')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    last_visit = models.DateTimeField('последнее посещение', default=timezone.now)
    pages_dict = models.JSONField('посещение страниц', default=dict)

class ForumPagesCounter(models.Model):
    page_url = models.CharField('url адрес страницы', max_length=100, blank=True)
    visited = models.IntegerField('количество посещений', default=0)

class ForumReadTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    last_view = models.DateTimeField('последний просмотр', default=timezone.now)