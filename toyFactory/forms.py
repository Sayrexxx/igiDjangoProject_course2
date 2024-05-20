from django import forms

from .models import MyUser, Review

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


class OrderForm(forms.Form):
    available_amount = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    amount = forms.IntegerField(min_value=1)

    def __init__(self, available_amount=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['available_amount'].initial = available_amount

    def clean(self):
        cleaned_data = super().clean()
        available_amount = cleaned_data.get('available_amount')
        amount = cleaned_data.get('amount')

        if available_amount is not None and amount > available_amount:
            raise forms.ValidationError(f"Amount cannot be greater than the available amount of {available_amount}.")

        return cleaned_data


class OrderDeleteForm(forms.Form):
    confirm_delete = forms.BooleanField(label='Confirm delete', required=True)


class PurchaseCreateForm(forms.Form):
    promo_code = forms.CharField(max_length=8, required=False)
    town = forms.CharField(max_length=50)


class PhoneNumberChangeForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['username']