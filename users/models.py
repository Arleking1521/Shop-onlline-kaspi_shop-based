from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    date_of_birth = models.DateField(default='2000-01-01', verbose_name='Дата рождения')
    phone = models.CharField(verbose_name='Номер телефона', unique=True)
    address = models.CharField(verbose_name='Адрес проживания', blank=True)
    password = models.CharField(verbose_name='Пароль')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}: {self.phone}'
