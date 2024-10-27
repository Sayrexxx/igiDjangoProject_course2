"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from django.conf import settings
from django.conf.urls.static import static

from toyFactory import views
from toyFactory.apiUsage import apiViews

from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_company, name='about'),
    path('news/', views.news, name='news'),
    path('terms/', views.terms, name='terms'),
    path('coupons/', views.coupons, name='coupons'),
    path('contacts/', views.contacts, name='contacts'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('add_review/', views.ReviewCreateView.as_view(), name='add_review'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('admin/', admin.site.urls),
    path('register_customer/', views.register_customer, name='register_customer'),
    path('register_employee/', views.register_employee, name='register_employee'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    re_path(r'user/?username=request.user.username/orders/', views.UserOrderListView.as_view(), name='user_orders'),  
    re_path(r'user/?username=request.user.username/edit_profile/', views.edit_profile_view, name='edit_profile'),  
    path('cat_facts', apiViews.cats, name='cat_facts'),
    path('random_joke', apiViews.random_joke, name='random_joke'),
    path('products/', views.ProductListView.as_view(), name='products'),
    re_path(r'orders/(?P<number>\d+)/cancel/', views.cancel_order, name='cancel_order'),   
    path('edit_order_status/<int:number>/', views.edit_order_status, name='edit_order_status'),
    
    # path('products/order/create/', views.OrderCreateView.as_view(), name='create_order'),

    path('orders/all/', views.get_all_orders, name='all_orders'),
    
    path('statistics/', views.category_percentage_view, name='statistics'),

    path('news/<int:article_id>/', views.article_detail, name='article_detail'),

    
    path('add_to_cart/<str:product_name>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', views.CartView.as_view(), name='cart_detail'),
    path('remove_from_cart/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)