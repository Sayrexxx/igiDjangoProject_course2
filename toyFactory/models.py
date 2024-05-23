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
    text = models.TextField()

    def __str__(self):
        return self.text


class Term(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
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
    delivery_point = PickUpPoint().address
    promo_code = models.CharField(max_length=8, null=True)
    
    STATUS_CHOICES = (
        ("В обработке ", "В обработке"),
        ("Принят", "Принят"),
        ("Доставлен", "Доставлен"),
        ("Отменён", "Отменён"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="В обработке")


    def __str__(self):
        return self.product.name

    def apply_promo(self, promo):
        if PromoUsage.objects.filter(user_id=self.user, promo_id=promo).exists():
            return
        self.price *= 1 - promo.discount/100
        self.promo_code = promo.code
        self.save()

        logging.warning(f'applied promo for {self.number} order')

        PromoUsage.objects.create(promo=promo, user=self.user)


class Purchase(models.Model):
    purchase_id = models.IntegerField(default=random.randint(1, 100000))
    user = models.ForeignKey(MyUser, related_name='purchases', on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    town = models.CharField(max_length=50)
    delivery_date = models.DateTimeField()

    def __str__(self):
        return self.order


class Promo(models.Model):
    code = models.CharField(max_length=8)
    discount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.code


class PromoUsage(models.Model):
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)