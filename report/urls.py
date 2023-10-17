from django.urls import path
from . import views

urlpatterns = [
    
    path('report/', views.getData, name='getData' ),
    path('report/view_report/', views.view_report, name='view_report' ),
    path('top_10/', views.top_10, name='top_10'),
]