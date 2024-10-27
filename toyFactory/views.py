from .models import *
from .forms import *
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Prefetch
from django.views.generic import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.db.models import Count
import matplotlib.pyplot as plt
import io
import urllib, base64

import requests
import logging

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages



logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s')


def getUserRole(name):
    if name != None:
        user = MyUser.objects.all().filter(username=name).first()
        if user != None:
            role = MyUser.objects.all().filter(username=name).first().role
            return role

def about_company(request):
    info = CompanyInfo.objects.first()
    logging.info(f'Company info: {info}')
    return render(request, 'about_company.html', {'info': info})

def home(request):
    first_of_news = Article.objects.first()
    name = request.user.username

    context = {
        'first_of_news': first_of_news,
        'getUserRole': getUserRole(name),
    }

    logging.info(f'news titles: {[first_of_news.title]}')
    return render(request, 'home.html', context)

def news(request):
    all_news = Article.objects.all()
    name = request.user.username

    context = {
        'all_news': all_news,
        'getUserRole': getUserRole(name),
    }

    logging.info(f'news titles: {[new.title for new in all_news]}')
    return render(request, 'news.html', context)


def terms(request):
    all_terms = DictionaryOfTerms.objects.all()
    for term in all_terms:
        term.summary = term.answer[:20] + "..."
        term.save()
    logger.info("Get the questions and answers")
    return render(request, "terms.html", {"all_terms": all_terms})


def contacts(request):
    all_contacts = MyUser.objects.all().filter(role='employee')
    logging.info(f'contacts names: {[contact.username for contact in all_contacts]}')
    return render(request, 'contacts.html', {'all_contacts': all_contacts})


def vacancies(request):
    all_vacancies = Vacancy.objects.all()
    logging.info(f'vacancies titles: {[vacancy.title for vacancy in all_vacancies]}')
    return render(request, 'vacancies.html', {'all_vacancies': all_vacancies})


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def random_fact(request):
    url = 'https://favqs.com/api/qotd'
    fact = requests.get(url.format()).json()
    return JsonResponse(fact, safe=False)


def random_joke(request):
    url = 'https://official-joke-api.appspot.com/random_joke'
    joke = requests.get(url.format()).json()
    return JsonResponse(joke, safe=False)


# class ReviewListView(ListView):
#     model = Review
#     queryset = Review.objects.all()
#     template_name = 'reviews.html'


def reviews(request):
    all_reviews = Review.objects.all()
    name = request.user.username

    context = {
        'object_list': all_reviews,
        'getUserRole': getUserRole(name)
    }

    logging.info(f'reviews: {[review.text for review in all_reviews]}')
    return render(request, 'reviews.html', context)


class ReviewCreateView(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            form = ReviewForm()
            return render(request, 'add_review.html', {'form': form})
        return redirect('login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            form = ReviewForm(request.POST)
            if form.is_valid():

                review = form.save(commit=False)
                logging.info(f'REQUEST_USER:{request.user}')
                # Create an instance but don't save to the database yet
                review.sender = request.user.username  # Associate the review with the logged-in user
                review.save()  # Save the instance to the database
                logging.info('Created Review object!')
                return redirect('reviews')
            else:
                logging.warning('Form invalid: %s', form.errors)
                return render(request, 'add_review.html', {'form': form})
        return redirect('login')


def register_customer(request):
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            authenticate(request)
            login(request, user)
            return redirect('home')
    else:
        form = CustomerUserCreationForm()
    return render(request, 'register.html', {'form': form})


def register_employee(request):
    if request.method == 'POST':
        form = EmployeeUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            authenticate(request)
            login(request, user)
            return redirect('home')
    else:
        form = EmployeeUserCreationForm()
    return render(request, 'register.html', {'form': form})


class BaseViewContextMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['title'] = kwargs.get('title', 'Default Title')
        return context


class LoginUser(BaseViewContextMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))


class LogoutUser(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')


def profile_view(request):
    name = request.user.username
    user = get_object_or_404(MyUser, id=request.user.id)
    context = {
        'status': getUserRole(name),
        'photo': user.image.url if user.image and user.role == 'employee' else None,
        'email': user.email,
        'age': user.age,
        'phone_number': user.phone_number,
        'description': user.description if user.role == 'employee' else '',
        'username': user.username,
        'edit_url': reverse('edit_profile'),
    }
    logging.info(f'Profile: {name}')
    return render(request, 'profile.html', context)

def edit_profile_view(request):
    user = request.user
    if not isinstance(user, MyUser):
        user = MyUser.objects.get(username=request.user.username)

    if getUserRole(user.username) == 'employee':
        form_class = EmployeeProfileForm
    else:
        form_class = CustomerProfileForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = form_class(instance=user)
    return render(request, 'edit_profile.html', {'form': form})


class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        return Product.objects.prefetch_related(
                    Prefetch('category', queryset=Category.objects.all().values_list('name'))
                )
    def get(self, request, *args, **kwargs):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        category_name = request.GET.get('cat_name')
        producer_name = request.GET.get('prod_name')

        products = self.filter_products(min_price, max_price, producer_name, category_name)


        logging.info(f'PRODUCT CATEGORIES: {[product.category.all() for product in products ]}')

        return render(request, 'products.html', {'products': products})

    @staticmethod
    def filter_products(min_price=None, max_price=None, prod_name=None, cat_name=None):
        products = Product.objects.prefetch_related('category')

        filtered_products = None

        if cat_name:
            if Category.objects.filter(name=cat_name).exists():
                category = Category.objects.get(name=cat_name)
                products = products.filter(category=category)
        if prod_name:
            if MyUser.objects.filter(role='employee', name=prod_name).exists():
                current_employee = MyUser.objects.filter(role='employee', name=prod_name)
                products = products.filter(employee=current_employee)

        if min_price is not None and max_price is not None:
            filtered_products = products.filter(price__gte=min_price, price__lte=max_price)
        elif min_price is not None:
            filtered_products = products.filter(price__gte=min_price)
        elif max_price is not None:
            filtered_products = products.filter(price__lte=max_price)

        if filtered_products is not None:
            return filtered_products
        return products


from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import MyUser, Product, Cart, Order, Promo
from .forms import OrderForm  # Убедитесь, что ваш файл форм содержит нужные формы
import logging


from django.shortcuts import render, redirect
from django.views import View
from .forms import OrderForm
from .models import MyUser, Cart, Product, Order, Promo
import logging
from django.utils import timezone
from datetime import timedelta

class OrderCreateView(View):
    def get(self, request, *args, **kwargs):
        warning_message_text = ""
        user = MyUser.objects.get(username=request.user.username)

        if request.user.is_authenticated and getUserRole(request.user.username) == 'customer':
            cart_items = Cart.objects.filter(user=user)
            if not cart_items.exists():
                warning_message_text = "Ваша корзина пуста. Пожалуйста, добавьте товары."
                return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})

            total_price = sum(item.get_price() for item in cart_items)
            products_forms = []
            
            for item in cart_items:
                product = item.product
                form = OrderForm(available_amount=product.amount)
                products_forms.append({'product': product, 'form': form, 'cart_item': item})

            return render(request, 'cart_detail.html', {
                'products_forms': products_forms,
                'total_price': total_price
            })
        else:
            warning_message_text = 'Пожалуйста, авторизуйтесь, чтобы оформить заказ'
        
        logging.warning(f'OrderCreateView GET: {warning_message_text}')
        return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})

    def post(self, request, *args, **kwargs):
        warning_message_text = ""
        if request.user.is_authenticated and getUserRole(request.user.username) == 'customer':
            cart_items = Cart.objects.filter(user=request.user)

            for item in cart_items:
                product = item.product
                form = OrderForm(request.POST, available_amount=product.amount)
                
                if form.is_valid():
                    amount = form.cleaned_data['amount']
                    delivery_date = form.cleaned_data['delivery_date']
                    promo_code = form.cleaned_data['promo_code']
                    delivery_point = form.cleaned_data['delivery_point']

                    price = product.price * amount
                    
                    # Проверка на наличие промокода
                    if promo_code:
                        try:
                            promo = Promo.objects.get(code=promo_code)
                            price *= (100 - promo.discount) / 100
                        except Promo.DoesNotExist:
                            warning_message_text = "Такого промокода нет"
                            logging.warning(f'Промокод не найден: {promo_code}')
                            break

                    # Создание заказа
                    Order.objects.create(
                        user=request.user,
                        product=product,
                        amount=amount,
                        price=price,
                        delivery_date=delivery_date,
                        delivery_point=delivery_point
                    )
                    
                    product.amount -= amount
                    product.save()
                    
                    logging.info('Создан заказ для пользователя %s: %s', request.user.username, product.name)
                    return redirect('news')

                else:
                    # Получение ошибок формы
                    warning_message_text = form.errors.as_text()
                    logging.warning(f'OrderForm validation errors: {warning_message_text}')

            if warning_message_text:
                logging.warning(f'OrderCreateView POST: {warning_message_text}')
                return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})

        else:
            warning_message_text = 'Пожалуйста, авторизуйтесь, чтобы оформить заказ'
        
        logging.warning(f'OrderCreateView POST: {warning_message_text}')
        return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})



class UserOrderListView(View):
    def get(self, request):
        warning_message_text = ""
        if request.user.is_authenticated :
            if not request.user.is_superuser:

                current_user = MyUser.objects.get(username=request.user.username)

                if getUserRole(request.user.username) == 'customer':
                    user_orders = Order.objects.all().filter(user=current_user)

                    if user_orders:
                        orders_data = []
                        for order in user_orders:
                            orders_data.append({
                                "number": order.number,
                                "price": order.price,
                                "point": order.delivery_point,
                                "status": order.status,
                            })
                            logging.info(f"ORDER NUMBER: {order.number}\nORDER DELIVERY POINT: {order.delivery_point}")
                        context = {
                            'orders': orders_data,
                            'getUserRole': getUserRole(current_user.username),
                        }
                        logging.info(f"ORDERS: {orders_data}")

                        logging.info("UserOrderListView: customer order list was successfully created")
                        return render(request, 'orders.html', context=context)
                    else:
                        warning_message_text = 'Нет заказов. Перейдите в каталог с товарами\n и найдите для себя что-нибудь интересное'
                else:
                    user_orders = Order.objects.filter(product__employee=current_user)
                    if user_orders:
                        orders_data = []
                        for order in user_orders:
                            product_name = order.product.name
                            orders_data.append({
                                "number": order.number,
                                "customer": order.user,
                                "product_name": product_name,
                                "amount": order.amount,
                                "price": order.price,
                                "date_created": order.date_created,
                                "delivery_date": order.delivery_date,
                                "delivery_point": order.delivery_point,
                                "promo_code": order.promo_code,
                                "status": order.status
                            })
                            logging.info(f"ORDER NUMBER: {order.number}")
                        context = {
                            'orders': orders_data,
                            'getUserRole': getUserRole(current_user.username),
                            'STATUS_CHOICES': order.STATUS_CHOICES
                        }
                        logging.info(f"ORDERS: {orders_data}")
                        logging.info("UserOrderListView: employee order list was successfully created")
                        return render(request, 'orders.html', context=context)
                    else:
                        warning_message_text = 'Для ваших товаров не найдено ни одного заказа'
        else:
            warning_message_text = 'Пожалуйста, авторизуйтесь для получения списка ваших заказов'
        logging.warning(f'UserOrderListView: {warning_message_text}')
        return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})


def cancel_order(request, number):
    order = get_object_or_404(Order, number=number)
    if request.method == 'POST':
        order.status = "Отменён"
        order.save()
    return redirect('user_orders')

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden

def edit_order_status(request, number):
    order = get_object_or_404(Order, number=number)
    if request.method == 'POST':
        selected_status = request.POST.get('status')
        if selected_status in dict(order.STATUS_CHOICES).keys():
            order.status = selected_status
            order.save()
            return redirect('user_orders')
        else:
            return HttpResponseForbidden("Неверный статус")
    return render(request, 'news.html')

def category_percentage_view(request):
    all_orders = Order.objects.all()
    category_counts = all_orders.values('product__category__name').annotate(count=Count('product__category__name'))
    total_orders = all_orders.count()

    category_names = []
    category_percentages = []
    for category in category_counts:
        percentage = (category['count'] / total_orders) * 100
        category_names.append(category['product__category__name'])
        category_percentages.append(percentage)

    plt.figure(figsize=(10, 6))
    plt.pie(category_percentages, labels=category_names, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    context = {
        'data': uri
    }

    return render(request, 'category_percentage.html', context)

def get_all_orders(request):
    user_orders = Order.objects.all()
    if user_orders:
        orders_data = []
        for order in user_orders:
            product_name = order.product.name
            orders_data.append({
                "number": order.number,
                "customer": order.user,
                "product_name": product_name,
                "amount": order.amount,
                "price": order.price,
                "date_created": order.date_created,
                "delivery_date": order.delivery_date,
                "delivery_point": order.delivery_point,
                "promo_code": order.promo_code,
                "status": order.status
            })
            logging.info(f"ORDER NUMBER: {order.number}")
        context = {
            'orders': orders_data,
            'STATUS_CHOICES': order.STATUS_CHOICES
        }
        logging.info(f"ORDERS: {orders_data}")
        return render(request, 'orders.html', context=context)
    else:
        warning_message_text = 'Для ваших товаров не найдено ни одного заказа'
    return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'article_detail.html', {'article': article})

def coupons(request):
    coupons = Promo.objects.all()
    logging.info(f'Coupons: {[coupon.code for coupon in coupons]}')
    return render(request, "coupons.html", {"coupons": coupons})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = get_object_or_404(MyUser, id=request.user.id)
    cart_item, created = Cart.objects.get_or_create(user=user, product=product, defaults={'amount': 1})
    if not created:
        cart_item.amount += 1
        cart_item.save()
    return redirect('products')

def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_price() for item in cart_items)
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})

@require_POST
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def checkout(request):
    # Fetch the actual MyUser instance
    user = MyUser.objects.get(pk=request.user.pk)

    cart_items = Cart.objects.filter(user=user)

    for item in cart_items:
        product = item.product
        # Add the user to the session participants
        session.participants.add(user)
        session.save()

    # Clear the cart after checkout
    cart_items.delete()

    messages.success(request, "Вы оформили заказ!")
    return redirect('registered_trainings_list')