# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='cycle_tracker/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('day/add/', views.CycleDayCreate.as_view(), name='add_day'),
    path('day/<int:pk>/edit/', views.CycleDayUpdate.as_view(), name='edit_day'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('settings/', views.settings_view, name='settings'),
    path('stats/', views.stats_view, name='stats'),
]