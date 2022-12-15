from django.db import models


class SitePage(models.Model):
    slug = models.SlugField('url', max_length=255, db_index=True, unique=True, default='', blank=True)
    alias = models.CharField('ссылка', max_length=20, default='', null=True, blank=True)
    title = models.CharField('название', max_length=200, null=True, blank=True)
    intro_text = models.TextField('краткое содержание страницы', null=True, blank=True, default='')
    content = models.TextField('содержание страницы', null=True, blank=True, default='')
    pub_date = models.DateField('дата создания')
    template = models.CharField('файл шаблона', max_length=100, null=False, blank=True, default='.html')
    context_model = models.CharField('контекст модели', max_length=50, default='', null=True, blank=True)
    use_in_menu = models.BooleanField()
    is_category = models.BooleanField()

    def __str__(self):
        return self.title + ' ' + str(self.pub_date)

    def get_absolute_url(self):
        host = 'http://127.0.0.1:8000/'
        return host + self.slug + '/' if self.slug else host
