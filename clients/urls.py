from django.urls import path

from . import views, machine

urlpatterns = [
    # path('', views.sign_in, name='login'),
    path('', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('dash/', views.dash, name='dash'),
    path('machine/initial/', machine.get_products_and_slots, name='machine_initial'),
]
