from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('', views.team_list_view, name='team_list'),
    path('create/', views.team_create_view, name='team_create'),
    path('edit/<int:pk>/', views.team_edit_view, name='team_edit'),
    path('delete/<int:pk>/', views.team_delete_view, name='team_delete'),
]
