from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_list_view, name='profile_list'),
    path('register/', views.profile_register_view, name='profile_register'),
    path('edit/<int:pk>/', views.profile_edit_view, name='profile_edit'),
    path('delete/<int:pk>/', views.profile_delete_view, name='profile_delete'),
    path('mbti/', views.mbti_view, name='mbti'),
]
