# carrito/models.py
from django.db import models
from django.contrib.auth.models import User
from blog.models import Articulo 
# Asumiendo que los productos están en la app 'tienda'


class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Articulo, through='ProductoCarrito', related_name='carritos')

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

class ProductoCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.producto.nombre} x {self.producto.precio} x {self.cantidad}"
    
class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Articulo, through='ProductoPedido')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.username} - {self.estado}"
    
class ProductoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


    