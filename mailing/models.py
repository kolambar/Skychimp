from django.utils.text import slugify
from unidecode import unidecode
from django.db import models


# Create your models here.


NULLABLE = {'blank': True, 'null': True}


class Mailin(models.Model):
    name = models.CharField(max_length=150, verbose_name='название рассылки', unique=True)
    slug = models.SlugField(unique=True, blank=True, verbose_name='название рассылки')
    mail_time = models.CharField(verbose_name='время рассылки')  # xx:xx / час:минута
    interval = models.CharField(verbose_name='интервал рассылки')  # xxxx-xx-xx / год-месяц-день
    status = models.BooleanField(verbose_name='запущена', default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(str(Mailin)))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name='ФИО')
    email = models.EmailField(unique=True, verbose_name='электронная почта')
    comment = models.TextField(verbose_name='комментарий', **NULLABLE)
    mailin = models.ManyToManyField(Mailin, verbose_name='рассылки')

    def __str__(self):
        return f'{self.name}, {self.email}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название/тема')
    text = models.TextField(verbose_name='текст')
    mailing = models.ForeignKey(Mailin, verbose_name='рассылка', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}, {self.mailing}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Attempts(models.Model):
    data_time = models.DateTimeField(verbose_name='дата и время')
    status = models.CharField(max_length=300, verbose_name='статус отправки')
    comment = models.TextField(verbose_name='ответ почтового сервиса', **NULLABLE)
    massage = models.ForeignKey(Message, verbose_name='сообщение')

    def __str__(self):
        return f'{self.data_time}, {self.status}, {self.massage}'

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
