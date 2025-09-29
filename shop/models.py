from django.db import models
from django.utils import timezone
from users.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Categories(models.Model):
    title = models.CharField(verbose_name='Название категории')
    image_link = models.ImageField(verbose_name='Картинка')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self) -> str:
        return f'{self.title} {self.image_link}'
    
class Sellers(models.Model):
    title = models.CharField(verbose_name='Название продавца')
    log_img = models.ImageField(verbose_name='Логотип', blank=True)
    phone_number = models.CharField(verbose_name='Номер телефона')
    reg_date = models.DateTimeField(verbose_name='Дата регистрации', auto_now=timezone.now())
    city = models.CharField(verbose_name='Город')

    class Meta:
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'
    
    def __str__(self) -> str:
        return f'{self.title} {self.phone_number} ({self.reg_date})'
    

class Subcategory(models.Model):
    title = models.CharField(verbose_name='Название подкатегории')
    base_specifications = models.TextField(verbose_name='Обязательные характеристики')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, verbose_name='Категория')

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self) -> str:
        return f'{self.title}'

class Product(models.Model):
    title = models.CharField(verbose_name='Продукт')
    description = models.TextField(verbose_name='Описание')
    subcat = models.ForeignKey(Subcategory, on_delete=models.CASCADE, verbose_name='Подкатегория')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
    
    def __str__(self) -> str:
        return f'{self.title}'

class Images(models.Model):
    image_link = models.ImageField(verbose_name='Картинка продукта')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')

    def __str__(self) -> str:
        return f'{self.product}'

class Sellers_prod(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продаваемые товары')
    seller = models.ForeignKey(Sellers, on_delete=models.CASCADE, verbose_name='Продавец')
    price = models.IntegerField(verbose_name='Цена')
    choice_btn = models.BooleanField(default=False, verbose_name='Наличие товара')

    class Meta:
        verbose_name = 'Продаваемый продукт'
        verbose_name_plural = 'Продаваемые продукты'
    
    def __str__(self) -> str:
        return f'{self.prod} {self.seller} {self.choice_btn}'

class Spec_category(models.Model):
    name = models.CharField(verbose_name='Название категории характеристики')

    class Meta:
        verbose_name = 'Категория характеристики'
        verbose_name_plural = 'Категории характеристик'
    
    def __str__(self) -> str:
        return f'{self.name}'

class Specification(models.Model):
    name = models.CharField(verbose_name='Название характеристики')
    subcat = models.ForeignKey(Subcategory, on_delete=models.CASCADE, verbose_name='Подкатегория товара')
    spec_cat = models.ForeignKey(Spec_category, on_delete=models.CASCADE, verbose_name='Категория характеристики')

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Все характеристики'
    
    def __str__(self) -> str:
        return f'{self.name}'


class Spec_vals(models.Model):
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, verbose_name='Характеристика продукта')
    values = models.CharField(verbose_name='Значение')
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'
    
    def __str__(self) -> str:
        return f'{self.specification.name} {self.values}'

    
class Review(models.Model):
    comment = models.TextField(verbose_name='Комментарий')
    rating = models.IntegerField(verbose_name='Рейтинг', validators=(
        MinValueValidator(0, 'Оценка не должна быть ниже 0'),
        MaxValueValidator(5, 'Оценка не должна превышать 5'),
        ))
    date = models.DateTimeField(auto_now=timezone.now(), verbose_name='Дата')
    sell_prod = models.ForeignKey(Sellers_prod,on_delete=models.CASCADE, verbose_name='Проданный товар')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Автор')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
    
    def __str__(self) -> str:
        return f'{self.author} {self.sell_prod} {self.rating} ({self.date})'