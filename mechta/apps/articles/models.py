from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField('название новости', max_length=200)
    text = models.TextField('текст новости')
    pub_date = models.DateField('дата публикации')

    def __str__(self):
        return self.title + ' ' + str(self.pub_date)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author_name = models.CharField('имя автора', max_length=50)
    text = models.CharField('комментарий', max_length=200)

    def __str__(self):
        return self.author_name
