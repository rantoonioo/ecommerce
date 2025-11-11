from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.lista_articulos, name='lista_articulos'),
    path('articulo/<int:pk>/', views.detalle_articulo, name='detalle_articulo'),
    path('crear/', views.crear_articulo, name='crear_articulo'),
    path('editar/<int:pk>/', views.editar_articulo, name='editar_articulo'),
    #url api
    path('articulos_api/', views.blog_api, name='blog_api'),
    path('articulo_api/<int:pk>/', views.blog_api_detalle, name='blog_api_detalle'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('productos-aleatorios/', views.mostrar_articulos_aleatorios, name='productos_aleatorios'),
    path('eliminar/<int:pk>/', views.eliminar_articulo, name='eliminar_articulo')
   
   

  
    

  



]
