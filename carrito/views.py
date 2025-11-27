# carrito/views.py
from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Carrito, ProductoCarrito
from blog.models import Articulo
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from blog.models import Producto  
import paypalrestsdk
from django.http import HttpResponse
from .models import Pedido, ProductoPedido
from decimal import Decimal

# Configuración de PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a 'live' en producción
    "client_id": "ATjAfWrVTTsN1FOeDDU1JEJUjNp4LBCSnQ-DkbLgUjXnrgqDLOS09XHPct1nShPjoBfzKzAHxL_21y85",
    "client_secret": "EBns3PV5n8gdKpCBTYW7LqfBojue07rhLPXM0CjJDlHXQIuxmzA45lH7MbzzeGXM8QLxRRhkc2kAZUL3",
})

@login_required
def ver_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if carrito:
        productos_carrito = ProductoCarrito.objects.filter(carrito=carrito)

        # Verificar que los productos existen antes de sumarlos
        total = 0
        for producto_carrito in productos_carrito:
            try:
                producto = producto_carrito.producto
                total += producto.precio * producto_carrito.cantidad
            except Articulo.DoesNotExist:
                # Si no existe el producto, lo manejamos y no sumamos nada
                continue

        return render(request, 'carrito/ver_carrito.html', {'productos_carrito': productos_carrito, 'carrito': carrito, 'total': total})

    return render(request, 'carrito/ver_carrito.html', {'mensaje': 'El carrito está vacío.'})

@login_required
def agregar_al_carrito(request, producto_id):
    # Obtiene el producto desde la base de datos
    producto = get_object_or_404(Articulo, id=producto_id)

    # Verificar si hay suficiente stock
    if producto.stock <= 0:
        # Si no hay stock, redirigir a la página del carrito o a una página de error
        return redirect('carrito:sin_stock')  # Asumiendo que tienes una vista para manejar esta situación

    # Obtener el carrito del usuario, o crear uno si no existe
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    # Verificar si el producto ya está en el carrito
    producto_carrito, creado = ProductoCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    
    if not creado:
        # Si el producto ya está en el carrito, aumentar la cantidad
        if producto.stock > producto_carrito.cantidad:
            producto_carrito.cantidad += 1
            producto_carrito.save()
        else:
            # Si no hay suficiente stock para agregar más, redirigir al usuario
            return redirect('carrito:sin_stock')

    # Redirigir a la página del carrito
    return redirect('carrito:ver_carrito')


@login_required
def eliminar_del_carrito(request, producto_id):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if carrito:
        producto_carrito = ProductoCarrito.objects.filter(carrito=carrito, producto__id=producto_id).first()
        if producto_carrito:
            producto_carrito.delete()
    return redirect('carrito:ver_carrito')



@login_required
def actualizar_cantidad(request, producto_carrito_id):
    try:
        # Obtener el producto en el carrito y la nueva cantidad
        producto_carrito = ProductoCarrito.objects.get(id=producto_carrito_id)
        nueva_cantidad = int(request.POST.get('cantidad'))
        
        # Asegurarnos de que la cantidad sea válida (mayor que 0)
        if nueva_cantidad < 1:
            return HttpResponseBadRequest("La cantidad debe ser mayor que 0.")
        
        # Actualizar la cantidad
        producto_carrito.cantidad = nueva_cantidad
        producto_carrito.save()

        return redirect('carrito:ver_carrito')  # Redirigir de vuelta al carrito
    except ProductoCarrito.DoesNotExist:
        return HttpResponseBadRequest("Producto no encontrado.")
    
def sin_stock(request):
    return render(request, 'carrito/sin_stock.html')


@login_required
def payment_view(request):
    """
    Vista para iniciar el pago con PayPal.
    """
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if carrito:
        # Calcular el total real del carrito
        total = 0
        for producto_carrito in carrito.productocarrito_set.all():
            producto = producto_carrito.producto
            total += producto.precio * producto_carrito.cantidad
        
        # Convertir el total a un formato adecuado (puedes usar Decimal si prefieres precisión)
        total_str = str(total)

        # Crear la transacción de PayPal con el total real
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {"total": total_str, "currency": "USD"},
                "description": "Pago por productos en el carrito",
            }],
            "redirect_urls": {
                "return_url": "http://52.15.203.101/carrito/success/",
                "cancel_url": "http://52.15.203.101/carrito/cancel/",
            },
        })

        if payment.create():
            # Redirige a la URL de aprobación de PayPal
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)  # Redirige al usuario a PayPal
        else:
            return HttpResponse(f"Error al crear el pago: {payment.error}")
    else:
        return HttpResponse("No hay productos en el carrito.")



def success_view(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            carrito = Carrito.objects.filter(usuario=request.user).first()
            if carrito:
                # Crear el pedido
                pedido = Pedido.objects.create(
                    usuario=request.user,
                    total=Decimal(payment.transactions[0].amount.total),
                    estado='pendiente'
                )
                productos_comprados = []

                # Procesar los productos en el carrito y crear los productos en el pedido
                for producto_carrito in carrito.productocarrito_set.all():
                    producto_pedido = ProductoPedido.objects.create(
                        pedido=pedido,
                        producto=producto_carrito.producto,
                        cantidad=producto_carrito.cantidad
                    )

                    # Reducir el stock del producto
                    producto = producto_carrito.producto
                    producto.stock -= producto_carrito.cantidad
                    producto.save()  # Guardar los cambios en el producto

                    # Agregar producto a la lista para mostrar en la página de éxito
                    productos_comprados.append({
                        'titulo': producto_carrito.producto.titulo,
                        'cantidad': producto_carrito.cantidad
                    })

                # Limpiar el carrito después de procesar el pedido
                carrito.productos.clear()

                # Pasar los productos comprados al contexto para mostrar en el perfil
                return render(request, 'carrito/success.html', {
                    'productos_comprados': productos_comprados,
                    'pedido': pedido
                })
        else:
            return HttpResponse(f"Error al procesar el pago: {payment.error}")
    return HttpResponse("El pago no fue exitoso.")

             

def cancel_view(request):
    """
    Vista para manejar el caso en que se cancele el pago.
    """
    return render(request, 'carrito/cancel.html')
