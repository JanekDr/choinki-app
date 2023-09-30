from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('success/', views.success_email_sent, name='success'),
    path('login/', views.user_login, name='login'),
    path('registration/', views.user_registration, name='registration'),
    path('customer/', views.customer, name='customer'),
    path('customer/<int:customerid>/<int:quantity>/', views.tree, name='tree'),
    path('customer/<int:customerid>/<str:treesids>/order-confirmation', views.order, name='order-confirmation'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search,name='search')
]