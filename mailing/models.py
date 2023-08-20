from django.utils.text import slugify
from unidecode import unidecode
from django.db import models


# Create your models here.


NULLABLE = {'blank': True, 'null': True}


class Mailin(models.Model):
    name = models.CharField(max_length=150, verbose_name='название рассылки', unique=True)
    slug = models.SlugField(unique=True, blank=True, verbose_name='название рассылки')
    mail_time = models.TimeField(verbose_name='время рассылки')
    


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'
