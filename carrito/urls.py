# carrito/urls.py

from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar_cantidad/<int:producto_carrito_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('sin_stock/', views.sin_stock, name='sin_stock'),

    path('pago/', views.payment_view, name='pago'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
   
    
    
]
