from warnings import WarningMessage
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
import datetime

from .models import *
from .forms import *

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

from django.utils import timezone

from django.urls import reverse, reverse_lazy



from django.views import View

from django.views.generic import *
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import login, logout, authenticate

from django.contrib.auth.views import LoginView

from django.db.models import F

import requests

import logging

logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s')


def getUserRole(name):
    if name != None:
        user = MyUser.objects.all().filter(username=name).first()
        if user != None:
            role = MyUser.objects.all().filter(username=name).first().role
            return role


def about_company(request):
    company_info_text = 'Toy Factory Company'
    logging.info(f'company info: {company_info_text}')
    return render(request, 'about_company.html', {'company_info_text': company_info_text})


def news(request):
    all_news = Article.objects.all()
    name = request.user.username
    
    context = {
        'all_news': all_news,
        'getUserRole': getUserRole(name)
    }
    
    logging.info(f'news titles: {[new.title for new in all_news]}')
    return render(request, 'news.html', context)


def terms(request):
    all_terms = Term.objects.all()
    logging.info(f'terms questions: {[term.question for term in all_terms]}')
    return render(request, 'terms.html', {'all_terms': all_terms})


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


# def login_user(request):
#     """
#     Logs in a user and redirects to the home page if successful.
#     """
#     form = LoginUserForm(request)
#     if request.method == 'POST':
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('home')
#                 else:
#                     logging.warning('Inactive user attempted to login')
#                     return HttpResponse('Error')
#             else:   
#                 logging.warning('Invalid login attempt')
#                 return HttpResponse('Invalid login')
#         else:
#             logging.warning('Invalid form submission')
#     return render(request, 'login.html', {'form': form})

class LogoutUser(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home') 


class UserListView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "employee":
            users = User.objects.filter(status="customer", is_superuser=False)

            users_data = []
            for user in users:
                users_data.append({
                    # "id": user.id,
                    "username": user.username,
                    "phone_number": user.phone_number,
                    "email": user.email,
                })
            return JsonResponse(users_data, safe=False)
        logging.warning('UserListView: page not found')
        return render(request, 'page_not_found.html', status=404)


class UserDetailView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "employee" and \
                User.objects.filter(pk=self.kwargs.get("pk"), is_superuser=False):
            pk = self.kwargs.get("pk")
            user = User.objects.get(pk=pk)
            if user.role != "employee":
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": user.phone_number,
                    "email": user.email,
                }
                return JsonResponse(user_data, safe=False)
            logging.warning('UserDetailView: page not found')
        return render(request, 'page_not_found.html', status=404)


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all()

    def get(self, request, *args, **kwargs):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        category_name = request.GET.get('cat_name')
        producer_name = request.GET.get('prod_name')

        products = self.filter_products(min_price, max_price, producer_name, category_name)

        products_data = []
        for product in products:
            categories = list(product.category.all().values_list('name', flat=True))

            products_data.append({
                'name': product.name,
                'price': product.price,
                'amount': product.amount,
                'category': categories,
                'producer_name': product.employee.username,
            })
        return render(request, 'products.html', {'products': products_data})

    @staticmethod
    def filter_products(min_price=None, max_price=None, prod_name=None, cat_name=None):
        products = Product.objects.all()

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


class ProductDetailView(DetailView):
    model = Product

    def get(self, request, *args, **kwargs):
        if Product.objects.filter(name=self.kwargs.get("name")).exists():
            product = Product.objects.all().filter(name=self.kwargs.get("name")).first()
            categories = list(product.category.all().values_list('name', flat=True))

            product_data = {
                'name': product.name,
                'price': product.price,
                'category': categories,
                'producer_name': product.employee.name,
                'producer_id': product.employee.id,
            }
            return render(request, 'product.html', {'product': product})
        logging.warning('ProductDetailView: page not found')
        return render(request, 'page_not_found.html', status=404)


class OrderCreateView(View):
    def get(self, request, current_product, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "customer" and \
                Product.objects.filter(name=current_product.name).exists():
            product = Product.objects.get(product=current_product)
            form = OrderForm()
            context = {
                'product': product,
                'form': form,
            }
            return render(request, 'order_form.html', context)
        logging.warning('OrderCreateView: page not found')
        return render(request, 'page_not_found.html', status=404)

    def post(self, request, current_product, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "customer" and \
                Product.objects.filter(name=current_product.name).exists():
            product = Product.objects.get(product=current_product)
            form = OrderForm(request.POST)

            if form.is_valid():
                amount = form.cleaned_data['amount']

                if product.amount - amount >= 0:
                    order = Order.objects.create(user=request.user, product=product, amount=amount,
                                                 price=amount * product.price)

                    order_data = {
                        "user": order.user.username,
                        "number": order.number,
                        "product_id": order.product.id,
                        "price": order.price,
                        "promo": order.promo_code,
                        "amount": order.amount,
                        "date": timezone.localtime(order.date),
                        "is_active": order.is_active,
                    }

                    product.amount -= amount
                    product.save()
                    logging.info('created Order object')
                    return JsonResponse(order_data, safe=False)
                return HttpResponse('There are not enough products in stock to place an order')
        elif request.user.is_authenticated and request.user.role == "employee":
            logging.warning('OrderCreateView: page not found')
            return render(request, 'page_not_found.html', status=404)
        else:
            logging.warning('OrderCreateView: user is not authenticated')
            return HttpResponse('please, login for making order!')


class OrderListView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            try:
                orders = Order.objects.all()

                orders_data = []
                for order in orders:
                    orders_data.append({
                        "user": order.user.username,
                        "number": order.number,
                        "product_id": order.product.id,
                        "price": order.price,
                        "promo": order.promo_code,
                        "amount": order.amount,
                        "date": timezone.localtime(order.date),
                        "is_active": order.is_active,
                    })
                return render(request, 'orders.html', {'orders': orders})
            except ObjectDoesNotExist:
                logging.warning('OrderListView: page not found')
                return render(request, 'page_not_found.html', status=404)
        logging.warning('OrderListView: page not found')
        return render(request, 'page_not_found.html', status=404)


class OrderDeleteDetailView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "employee" \
                and Order.objects.filter(pk=self.kwargs.get("pk")).exists():
            pk = self.kwargs.get("pk")
            order = Order.objects.get(pk=pk)

            order_data = {
                "user": order.user.username,
                "number": order.number,
                "product_id": order.product.id,
                "price": order.price,
                "promo": order.promo_code,
                "amount": order.amount,
                "date": timezone.localtime(order.date),
                "is_active": order.is_active,
            }
            return JsonResponse(order_data, safe=False)
        elif request.user.is_authenticated and request.user.role == "customer" \
                and Order.objects.filter(pk=self.kwargs.get("pk"), user_id=request.user.id).exists():
            pk = self.kwargs.get("pk")
            order = Order.objects.get(pk=pk, user_id=request.user.id)
            form = OrderDeleteForm()
            return render(request, 'order_detail.html', {'form': form, 'order': order})
        logging.warning('OrderDeleteView: page not found')
        return render(request, 'page_not_found.html', status=404)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "customer" \
                and Order.objects.filter(pk=self.kwargs.get("pk"), is_active=True).exists():
            form = OrderDeleteForm(request.POST)

            if form.is_valid():
                order_id = self.kwargs.get("pk")
                order = Order.objects.filter(pk=order_id, user=request.user).first()

                if order:
                    order_data = {
                        "user": order.user.username,
                        "number": order.number,
                        "product_id": order.product.id,
                        "price": order.price,
                        "promo": order.promo_code,
                        "amount": order.amount,
                        "date": timezone.localtime(order.date),
                        "is_active": order.is_active,
                    }
                    order.product.amount = F('amount') + order.amount
                    order.product.save()
                    order.delete()
                    logging.warning('deleted Order object')
                    return JsonResponse(order_data, safe=False)
        logging.warning('OrderDeleteView: page not found')
        return render(request, 'page_not_found.html', status=404)


class UserOrderListView(View):
    def get(self, request):
        warning_message_text = ""
        if request.user.is_authenticated and getUserRole(request.user.username) == 'customer':
            current_user = MyUser.objects.all().filter(username=request.user.username).first()
            user_orders = Order.objects.all().filter(user=current_user)
            logging.info(f'Заказы для пользователя {MyUser.username}: {[user_order.number for user_order in user_orders]}') 

            if user_orders:
                orders_data = []
                for order in user_orders:
                    orders_data.append({
                        "number": order.number,
                        "price": order.price,
                    })
                logging.info("UserOrderListView: user order list was successfully created")
                return render(request, 'orders.html', {'orders': orders_data})
            else:
                warning_message_text = 'Нет заказов. Перейдите в каталог с товарами\n и найдите для себя что-нибудь интересное'
        else:
            warning_message_text = 'Пожалуйста, авторизуйтесь для получения списка ваших заказов'
        logging.warning(f'UserOrderListView: {warning_message_text}')
        return render(request, 'warning_message.html', {'warning_message_text': warning_message_text})            


class PurchaseCreateView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "customer" \
                and Order.objects.filter(pk=self.kwargs.get("pk"), user=request.user, is_active=True).exists():
            order = Order.objects.get(pk=pk)
            form = PurchaseCreateForm()
            context = {
                'order': order,
                'form': form,
            }
            return render(request, 'purchase_form.html', context)
        logging.warning('PurchaseCreateView: page not found')
        return render(request, 'page_not_found.html', status=404)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "customer" \
                and Order.objects.filter(pk=self.kwargs.get("pk"), user=request.user, is_active=True).exists():
            form = PurchaseCreateForm(request.POST)

            if form.is_valid():
                pk = self.kwargs.get("pk")
                order = Order.objects.get(pk=pk, user=request.user, is_active=True)

                delivery_datetime = datetime.datetime.now() + datetime.timedelta(days=1)
                delivery_datetime = delivery_datetime.replace(hour=17, minute=0, second=0, microsecond=0)

                promo_code = form.cleaned_data["promo_code"]
                promo = Promo.objects.filter(code=promo_code).first()

                if promo:
                    order.apply_promo(promo)

                purchase = Purchase.objects.create(
                    user=request.user,
                    order=order,
                    town=form.cleaned_data["town"],
                    delivery_date=delivery_datetime
                )

                order.is_active = False
                order.save()

                logging.info('created Purchase object')

                purchase_data = {
                    "order_id": order.number,
                    "user_id": request.user.id,
                    "town": form.cleaned_data["town"],
                    "purchase_date": timezone.localtime(purchase.purchase_date),
                    "delivery_date": purchase.delivery_date,
                }
                return JsonResponse(purchase_data, safe=False)
        logging.warning('PurchaseCreateView: page not found')
        return render(request, 'page_not_found.html', status=404)


class PurchaseListView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "employee":
            try:
                purchases = Purchase.objects.all()

                purchases_data = []
                for purchase in purchases:
                    purchases_data.append({
                        "order_id": purchase.order.number,
                        "user_id": purchase.order.user.id,
                        "username": purchase.order.user.username,
                        "town": purchase.town,
                        "purchase_date": timezone.localtime(purchase.purchase_date),
                        "delivery_date": timezone.localtime(purchase.delivery_date),
                    })
                return JsonResponse(purchases_data, safe=False)
            except ObjectDoesNotExist:
                logging.warning('PurchaseListView: page not found')
                return render(request, 'page_not_found.html', status=404)
        logging.warning('purchaseListView: page not found')
        return render(request, 'page_not_found.html', status=404)


class PurchaseDetailView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "employee" \
                and Purchase.objects.filter(pk=self.kwargs.get("pk")).exists():
            pk = self.kwargs.get("pk")
            purchase = Purchase.objects.get(pk=pk)

            purchase_data = {
                "order_id": purchase.order.number,
                "user_id": purchase.order.user.id,
                "username": purchase.order.user.username,
                "town": purchase.town,
                "purchase_date": timezone.localtime(purchase.purchase_date),
                "delivery_date": timezone.localtime(purchase.delivery_date),
            }
            return JsonResponse(purchase_data, safe=False)
        elif request.user.is_authenticated and request.user.role == "customer" \
                and Purchase.objects.filter(pk=self.kwargs.get("pk"), user_id=request.user.id).exists():
            pk = self.kwargs.get("pk")
            purchase = Purchase.objects.get(pk=pk, user_id=request.user.id)

            purchase_data = {
                "order_id": purchase.order.number,
                "user_id": purchase.order.user.id,
                "username": purchase.order.user.username,
                "town": purchase.town,
                "purchase_date": timezone.localtime(purchase.purchase_date),
                "delivery_date": timezone.localtime(purchase.delivery_date),
            }
            return JsonResponse(purchase_data, safe=False)
        logging.warning('PurchaseDetailView: page not found')
        return render(request, 'page_not_found.html', status=404)


class PromoListView(View):
    def get(self, request, *args, **kwargs):
        promos = Promo.objects.all()
        promos_data = []

        for promo in promos:
            promos_data.append({
                "code": promo.code,
                "discount": promo.discount,
            })
        return JsonResponse(promos_data, safe=False)


class PickUpPointListView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pick_up_points = PickUpPoint.objects.all()
            if pick_up_points:
                pick_up_points_data = []
                for pick_up_point in pick_up_points:
                    pick_up_points_data.append({
                        'address': pick_up_point.address,
                    })
                return JsonResponse(pick_up_points_data, safe=False)
            logging.warning('PickUpPointsListView: no pick up points')
            return render(request, 'page_not_found.html', status=404)
        logging.warning('PickUpPointsListView: page not found')
        return render(request, 'page_not_found.html', status=404)