from datetime import timedelta
import uuid

from django.utils import timezone
import random
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

import re

import logging

logger = logging.getLogger(__name__)


class Article(models.Model):
    title = models.CharField(max_length=100, default='')
    content = models.TextField(default='')
    image = models.ImageField(upload_to='images/')
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CompanyInfo(models.Model):
    name = models.CharField(default='', max_length=255, verbose_name="Название компании")
    description = models.TextField(default='', verbose_name="Описание компании")  # Set a default value
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Логотип компании")
    video = models.URLField(null=True, blank=True, verbose_name="Видео о компании")
    history = models.TextField(null=True, blank=True, verbose_name="История по годам")
    requisites = models.TextField(null=True, blank=True, verbose_name="Реквизиты")
    certificate = models.TextField(null=True, blank=True, verbose_name="Сертификаты")

    def __str__(self):
        return self.name


class DictionaryOfTerms(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.TextField()
    summary = models.CharField(max_length=40, default='')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        """
        String for representing the DictionaryOfTerms object.
        """
        return self.question

class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Review(models.Model):
    sender = models.CharField(max_length=50, default='test')
    
    
    rating = models.IntegerField()
    text = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True)

    # def __str__(self):
    #     return self.sender.name


# class User(AbstractUser):
#     STATUS_CHOICES = (
#         ("employee", "employee"),
#         ("customer", "customer"),
#     )
#     status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="customer")
#     phone_number = models.CharField(max_length=13)
#     age = models.PositiveSmallIntegerField(default=100)
#     groups = models.ManyToManyField(Group, related_name='toyfactory_users')
#     user_permissions = models.ManyToManyField(
#         Permission, related_name='toyfactory_users_permissions'
#     )


#     def __str__(self):
#         return self.first_name

#     def save(self, *args, **kwargs):
#         phone_number_pattern = re.compile(r'\+375(25|29|33)\d{7}')
#         if not re.fullmatch(phone_number_pattern, str(self.phone_number)) or self.age < 18 or self.age > 100:
#             logger.exception("ValidationError")
#             raise ValidationError("Error while creating user")
#         super().save(*args, **kwargs)

class MyUser(User):
    ROLE_CHOICES = (
        ("employee", "employee"),
        ("customer", "customer"),
    )
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default="customer")
    phone_number = models.CharField(max_length=13)
    age = models.PositiveSmallIntegerField(default=30)
    
    
    user_ptr = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True, primary_key=True, default=None)
    
    
    image = models.ImageField(upload_to='images/')
        
    description = models.CharField(max_length=1000, default='')
    secret_key = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ManyToManyField(Category, related_name='products')
    employee = models.ForeignKey(MyUser, related_name='products', on_delete=models.CASCADE,  limit_choices_to={'role': 'employee'}, default=None)
    price = models.FloatField()
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class PickUpPoint(models.Model):
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.address
    
    
class Promo(models.Model):
    code = models.CharField(max_length=8)
    discount = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.code
    

class Order(models.Model):
    user = models.ForeignKey(MyUser, related_name='orders', on_delete=models.CASCADE)
    number = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(default=1)
    price = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(
        default=timezone.now() + timedelta(days=3)
    )    
    delivery_point = models.CharField(max_length=50, blank=True)
    promo_code = models.CharField(max_length=8, blank=True)
            
    STATUS_CHOICES = (
        ("В обработке ", "В обработке"),
        ("Принят", "Принят"),
        ("Доставлен", "Доставлен"),
        ("Отменён", "Отменён"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="В обработке")


    def __str__(self):
        return self.product.name


class Cart(models.Model):
    user = models.ForeignKey('MyUser', on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    def get_price(self):
        if self.product and self.product.price:
            return (self.amount * self.product.price)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"