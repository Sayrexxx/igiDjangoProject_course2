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

from toyFactory import statistic_views


from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', views.news, name='home'),
    path('about/', views.about_company, name='about'),
    path('news/', views.news, name='news'),
    path('terms/', views.terms, name='terms'),
    path('contacts/', views.contacts, name='contacts'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('add_review/', views.ReviewCreateView.as_view(), name='add_review'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),

    path('price_list', statistic_views.price_list, name='price_list'),
    path('customers', statistic_views.customers, name='customers'),
    path('demand_analysis', statistic_views.demand_analysis, name='demand_analysis'),
    path('monthly_sales_volume', statistic_views.monthly_sales_volume, name='monthly_sales_volume'),
    path('linear_trend', statistic_views.linear_sales_trend, name='linear_trend'),

    path('admin/', admin.site.urls),
    path('register_customer/', views.register_customer, name='register_customer'),
    path('register_employee/', views.register_employee, name='register_employee'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('products/', views.ProductListView.as_view(), name='products'),
    re_path(r'products/(?P<product_id>\d+)/$', views.ProductDetailView.as_view(), name='product'),
    re_path(r'products/(?P<product_id>\d+)/order/create/', views.OrderCreateView.as_view(), name='create_order'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    re_path(r'orders/(?P<number>\d+)/$', views.OrderDeleteDetailView.as_view(), name='order'),
    path('users/', views.UserListView.as_view(), name='users'),
    re_path(r'users/(?P<username>\d+)/$', views.UserDetailView.as_view(), name='user'),
    
    
    # ORDER FOR CURRENT USER
    re_path(r'user/?username=request.user.username/orders/', views.UserOrderListView.as_view(), name='user_orders'),
    
    
    
    re_path(r'orders/(?P<username>\d+)/purchase/create/', views.PurchaseCreateView.as_view(), name='create_purchase'),
    path('purchases/', views.PurchaseListView.as_view(), name='purchases'),
    re_path(r'purchases/(?P<purchase_id>\d+)/$', views.PurchaseDetailView.as_view(), name='purchase'),
    path('promos/', views.PromoListView.as_view(), name='promos'),
    path('pick_up_points/', views.PickUpPointListView.as_view(), name='pick_up_points'),
    
    
    path('cat_facts', apiViews.cats, name='cat_facts'),
    path('random_joke', apiViews.random_joke, name='random_joke')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)