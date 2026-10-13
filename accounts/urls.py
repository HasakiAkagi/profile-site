from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_register_view, name='signup'),
    path('register/', views.user_register_view, name='user_register'),
    path('', views.login_view, name='login'),
    path('menu/', views.menu_view, name='menu'),
    path('userinfo/register/', views.user_info_register_view, name='user_info_register'),
    path('userinfo/edit/', views.user_info_edit_view, name='user_info_edit'),
    path('delete/', views.user_delete_view, name='user_delete'),
    path('logout/', views.logout_view, name='logout'),
]
