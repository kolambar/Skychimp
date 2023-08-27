from django.utils.text import slugify
from unidecode import unidecode
from django.db import models


# Create your models here.


NULLABLE = {'blank': True, 'null': True}


class Message(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название/тема')
    text = models.TextField(verbose_name='текст')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailin(models.Model):

    INTERVAL_CHOICES = (
        ('daily', 'ежедневно'),
        ('weekly', 'еженедельно'),
        ('monthly', 'ежемесячно'),
    )

    STATUS_CHOICES = (
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('pending', 'В ожидании'),
    )

    name = models.CharField(max_length=150, unique=True, verbose_name='название рассылки')
    slug = models.SlugField(unique=True, blank=True, verbose_name='slug')
    start_time = models.DateTimeField(verbose_name='время старта рассылки', **NULLABLE)
    finish_time = models.DateTimeField(verbose_name='время остановки рассылки', **NULLABLE)
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, verbose_name='интервал рассылки')
    status = models.CharField(max_length=10, blank=True, default='pending', verbose_name='статус')
    message = models.ForeignKey(Message, verbose_name='рассылка', on_delete=models.CASCADE, **NULLABLE)

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(str(self.name)))
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


class AttemptsLog(models.Model):
    lust_time = models.DateTimeField(verbose_name='дата и время', auto_now_add=True)
    status = models.BooleanField(verbose_name='статус отправки')
    comment = models.TextField(verbose_name='ответ почтового сервиса', **NULLABLE)
    massage = models.ForeignKey(Message, verbose_name='сообщение', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.lust_time}, {self.status}, {self.massage}'

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
