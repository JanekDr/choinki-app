from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('success/', views.success_email_sent, name='success'),
    path('login/', views.user_login, name='login'),
    path('registration/', views.user_registration, name='registration'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('add_customer/<int:customerid>/<int:quantity>/', views.tree, name='tree'),
    path('add_customer/<int:customerid>/<str:treesids>/order-confirmation', views.order, name='order-confirmation'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search,name='search'),
    path('order-info/<int:pk>', views.order_info, name='order-info'),
    path('edit_customer/<int:pk>', views.edit_customer, name='edit_customer'),
    path('edit_trees/<int:pk>', views.edit_trees, name='edit_trees'),

]