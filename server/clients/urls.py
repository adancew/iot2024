from django.urls import path

from . import views, machine


urlpatterns = [
    # path('', views.sign_in, name='login'),
    path('', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    #path('dash/', views.dash, name='dash'), # old dashboard link
    path('machine/initial/', machine.get_products_and_slots, name='machine_initial'),

    path('owners/', views.dash, name='dash'),

    path('owners/transactions/', views.transactions, name='transaction-index'),

    path('owners/cards/', views.cards, name='card-index'),
    path('owners/cards/add', views.cards_add, name='card-add'),
    path('owners/cards/<int:card_id>/edit', views.cards_edit, name='card-edit'),
    path('owners/cards/<int:card_id>/delete', views.cards_delete, name='card-delete'),

    path('owners/products/', views.products, name='product-index'),
    path('owners/products/add', views.products_add, name='product-add'),
    path('owners/products/<int:product_id>/edit', views.products_edit, name='product-edit'),
    path('owners/products/<int:product_id>/delete', views.products_delete, name='product-delete'),

    path('owners/clients/', views.clients, name='client-index'),
    path('owners/clients/add', views.clients_add, name='client-add'),
    path('owners/clients/<int:client_id>/edit', views.clients_edit, name='client-edit'),
    path('owners/clients/<int:product_id>/delete', views.clients_delete, name='client-delete'),

    path('owners/vmachines/', views.vmachines, name='vmachine-index'),
    path('owners/vmachines/<str:vmachine_id>/edit/', views.vmachines_edit, name='vmachine-edit'),
    path('owners/vmachines/add/', views.vmachines_add, name='vmachine-add'),
    path('owners/vmachines/<str:vmachine_id>/delete/', views.vmachines_delete, name='vmachine-delete'),

    path('owners/vmachines/<str:vmachine_id>/slots/add', views.slots_add, name='slot-add'),
    path('owners/vmachines/<str:vmachine_id>/slots/<int:slot_id>/edit', views.slots_edit, name='slot-edit'),
    path('owners/vmachines/<str:vmachine_id>/slots/<int:slot_id>/delete', views.slots_delete, name='slot-delete'),

]

