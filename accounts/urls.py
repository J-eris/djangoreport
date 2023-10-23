from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('reset_password/', views.reset, name='reset_password'),
    path('reset_password_api/', views.reset_password_api, name='reset_password_api'),
]