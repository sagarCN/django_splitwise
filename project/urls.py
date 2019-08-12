from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'categories', views.categoriesViewset)

urlpatterns = [
    path(r'accounts/signup/', views.signup),
    path(r'accounts/signin/', views.signin),
    path(r'accounts/signout/', views.signout),
    path(r'expenses/', views.expense),
    path(r'balances/', views.balances),
    path(r'settle/', views.settle),
    path(r'expenses/<int:e_id>/', views.expense_id),
    path(r'users/<int:u_id>/balances/', views.balances_id),
    path(r'users/profile/', views.profile),
    url(r'^', include(router.urls))
]
