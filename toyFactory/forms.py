from datetime import timedelta
from django.utils import timezone
from django import forms
from requests import request

from .models import MyUser, Review, Order, PickUpPoint
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


from django.conf import settings

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django import forms
from django.utils.translation import gettext_lazy as _

import re

import logging

logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s')


class ReviewForm(forms.ModelForm):
    
    rating = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['rating', 'text']


# class RegisterUserForm(UserCreationForm):
#     phone_number = forms.CharField(max_length=13)
#     age = forms.IntegerField(min_value=0, max_value=200, initial=100)
#     status = 'customer'

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'age']
        
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.status = self.status
#         user.phone_number = self.cleaned_data['phone_number']
#         user.age = self.cleaned_data['age']

#         if commit:
#             user.save()
#             # Добавляем пользователя в группу "toyfactory_users"
#             group, _ = Group.objects.get_or_create(name='toyfactory_users')
#             user.groups.add(group)

#         return user
#     #username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
#     #password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
#     #password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


phone_number_pattern = re.compile(r'\+375(25|29|33|44)\d{7}')

class CustomerUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=13, required=True)
    age = forms.IntegerField(min_value=18, required=True)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'phone_number', 'age', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number_pattern.match(phone_number):
            raise forms.ValidationError("Неверный формат номера телефона. Пожалуйста, введите номер в формате +375(25|29|33)XXXXXXX.")
        return phone_number

    def save(self, commit=True):
        user = super(CustomerUserCreationForm, self).save(commit=False)
        user.role = 'customer'
        if commit:
            user.save()
        return user
    
    
class EmployeeUserCreationForm(UserCreationForm):
    secret_key = forms.CharField(widget=forms.PasswordInput)
    description = forms.CharField(max_length=1000, required=True)
    # phone_number = forms.CharField(max_length=13, required=True)
    # email = forms.EmailField(max_length=40, required=True)
    image = forms.ImageField(required=True)


    class Meta:
        model = MyUser
        fields = ('secret_key', 'username', 'email', 'phone_number', 'description', 'age', 'password1', 'password2', 'image')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        check_secret_key = self.cleaned_data['secret_key']
        if not phone_number_pattern.match(phone_number):
            raise forms.ValidationError("Неверный формат номера телефона. Пожалуйста, введите номер в формате +375(25|29|33)XXXXXXX.")
        if not check_secret_key == settings.SECRET_KEY_FOR_USER:
            raise forms.ValidationError("Неверный secret key. Пожалуйста обратитесь к\n"
                                        "администрации для получения валидного ключа")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.image = self.cleaned_data['image']
        user.role = 'employee'
        logging.info(user.__dict__)
            
        if commit:
            user.save()
            # Добавляем пользователя в группу "toyfactory_employees"
            # group, created = Group.objects.get_or_create(name='toyfactory_employees')
            # user.groups.add(group)
        return user



class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


from django.forms import ModelForm


class OrderForm(ModelForm):
    promo_code = forms.CharField(max_length=8, required=False)
    delivery_point = forms.ChoiceField(
        choices=[(address, address) for address in PickUpPoint.objects.values_list('address', flat=True)],
        label='Выберите пункт самовывоза'
    )
    
    class Meta:
        model = Order
        fields = ['delivery_date', 'delivery_point', 'promo_code']
        widgets = {
            'delivery_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']
        user_time_zone = timezone.get_current_timezone()
        delivery_date_user_tz = timezone.localtime(delivery_date, user_time_zone)
    
        if delivery_date_user_tz < timezone.now() + timedelta(days=3):
            raise ValidationError("Заказ можно будет забрать МИНИМУМ через 3 дня")
        return delivery_date_user_tz
    
    def clean_promo_code(self):
        promo_code = self.cleaned_data['promo_code']
        if promo_code and len(promo_code) > 8:
            raise ValidationError("Длина промокода не может превышать 8 символов")
        return promo_code

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['image', 'email', 'phone_number', 'description']


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['email', 'phone_number']


from django import forms

class CartForm(forms.Form):
    delivery_point = forms.ChoiceField(
        choices=[(address, address) for address in PickUpPoint.objects.values_list('address', flat=True)],
        label='Выберите пункт самовывоза'
    )
    delivery_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    promo_code = forms.CharField(max_length=8, required=False)

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']
        user_time_zone = timezone.get_current_timezone()
        delivery_date_user_tz = timezone.localtime(delivery_date, user_time_zone)
    
        if delivery_date_user_tz < timezone.now() + timedelta(days=3):
            raise forms.ValidationError("Заказ можно будет забрать МИНИМУМ через 3 дня")
        return delivery_date_user_tz
