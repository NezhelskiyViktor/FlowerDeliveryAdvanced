from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('register/', views.register, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),  # Страница входа
    path('logout/', views.logout_view, name='logout'),  # Функция для выхода
    path('showcase/', views.showcase, name='showcase'),  # Страница витрины/каталога для заказчиков
    path('cart/', views.cart, name='cart'),  # Страница корзины для заказа
    path('orders/', views.order_history, name='orders'),  # Страница истории заказов
    path('adminka/', views.login_admin, name='adminka'),  # Страница входа администратора
    path('home_admin/', views.home_admin, name='home_admin'),  # Страница администратора
]
