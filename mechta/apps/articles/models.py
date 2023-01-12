from django.db import models

# Create your models here.
class Article(models.Model):
    slug = models.SlugField('url', max_length=255, db_index=True, unique=True, default='', blank=True)
    title = models.CharField('название новости', max_length=200)
    text = models.TextField('текст новости')
    pub_date = models.DateField('дата публикации')

    def __str__(self):
        return self.title + ' ' + str(self.pub_date)

    def get_absolute_url(self):
        host = 'http://127.0.0.1:8000/'
        return host + '/articles/' + self.slug + '/'

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author_name = models.CharField('имя автора', max_length=50)
    text = models.CharField('комментарий', max_length=200)

    def __str__(self):
        return self.author_name
