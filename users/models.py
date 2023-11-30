from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')

    phone = models.CharField(max_length=20, verbose_name='номер телефона', **NULLABLE)
    country = models.CharField(max_length=58, verbose_name='название страны', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)

    verified = models.BooleanField(default=False, verbose_name='верифицирован', blank=True)
    verified_password = models.IntegerField(verbose_name='ключ для верификации')

    telegram = models.URLField(verbose_name='ссылка на телеграмм', **NULLABLE, max_length=200)
    telegram_id = models.CharField(verbose_name='id телеграмма', **NULLABLE)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
