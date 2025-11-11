from django.db import models
from django.contrib.auth.models import User

class Articulo(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True) 
    stock = models.PositiveIntegerField(default=0)  # Nuevo campo para controlar el stock.
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='articulos/', null=True, blank=True)  # Agregar este campo para la imagen
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Campo precio agregado
    cantidad = models.IntegerField(default=1)  # Este campo debe existir si se utiliza.
    
   
    
    def __str__(self):
        return self.titulo
    
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.IntegerField(default=0)  # Campo de stock con valor predeterminado de 0
    
    def __str__(self):
        return self.nombre
