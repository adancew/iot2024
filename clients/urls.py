from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('dash/', views.dash, name='dash'),
]