from django.db import models

# Create your models here.


NULLABLE = {'blank': True, 'null': True}


class Blog(models.Model):
    header = models.CharField(max_length=100, verbose_name='Заголовок', unique=True)
    slug = models.CharField(max_length=100, verbose_name='slug', **NULLABLE)
    text = models.TextField(verbose_name='Содержание')
    image = models.ImageField(upload_to='catalog/', verbose_name='Изображение', **NULLABLE)
    creation_date = models.DateField(verbose_name='Дата создания', auto_now_add=True)
    is_published = models.BooleanField(default=True, verbose_name='опубликовано')
    views_number = models.IntegerField(default=0, verbose_name='количество просмотров')

    def __str__(self):
        return f'{self.header}, {self.creation_date}'

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
