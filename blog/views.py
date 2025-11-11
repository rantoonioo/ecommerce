from django.shortcuts import render, redirect, get_object_or_404
from .models import Articulo
from django.db.models import Q
from .models import Producto
from .forms import ArticuloForm
Articulo.objects.all()


from django.contrib.auth.decorators import login_required

from django.shortcuts import render


def mostrar_articulos_aleatorios(request):
    # Obtener 3 artículos aleatorios
    articulos_aleatorios = Articulo.objects.all().order_by('?')[:3]

    # Pasar los artículos aleatorios al contexto
    context = {
        'articulos_aleatorios': articulos_aleatorios,
    }
    
    return render(request, 'index.html', context)

def producto_detalle(request, pk):
    producto = Producto.objects.get(pk=pk)
    return render(request, 'blog/producto_detalle.html', {'producto': producto})

def lista_articulos(request):
    query = request.GET.get('q', '')  # Obtén el término de búsqueda desde la URL (si existe)
    
    if query:  # Si hay un término de búsqueda
        articulos = Articulo.objects.filter(
            Q(titulo__icontains=query) |
            Q(descripcion__icontains=query)
        ).order_by('-fecha_publicacion')
    else:  # Sin búsqueda, mostrar todos los artículos
        articulos = Articulo.objects.all().order_by('-fecha_publicacion')

    # Pasar 'query' al contexto para el formulario
    return render(request, 'blog/lista_articulos.html', {'articulos': articulos, 'query': query})

def detalle_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    return render(request, 'blog/detalle_articulo.html', {'articulo': articulo})




def crear_articulo(request):
    if request.user.perfil.rol in ['editor', 'administrador']:
        if request.method == 'POST':
            form = ArticuloForm(request.POST, request.FILES)  # Asegúrate de pasar request.FILES para la imagen
            if form.is_valid():
                articulo = form.save(commit=False)
                articulo.autor = request.user
                articulo.save()
                return redirect('blog:detalle_articulo', pk=articulo.pk)
        else:
            form = ArticuloForm()
        return render(request, 'blog/crear_articulo.html', {'form': form})
    else:
        return redirect('blog:lista_articulos')



@login_required
def editar_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)

    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES, instance=articulo)
        if form.is_valid():
            form.save()
            return redirect('blog:detalle_articulo', pk=articulo.pk)
    else:
        form = ArticuloForm(instance=articulo)

    return render(request, 'blog/editar_articulo.html', {'form': form, 'articulo': articulo})
    
@login_required
def eliminar_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)

    # Verificar que el usuario sea el autor o administrador
    if request.user == articulo.autor or request.user.perfil.rol == 'administrador':
        articulo.delete()
        return redirect('blog:lista_articulos')  # Redirigir a la lista de artículos después de la eliminación

    # Si el usuario no tiene permiso, redirige a la página de lista sin eliminar
    return redirect('blog:lista_articulos')

    
    
    
from rest_framework.response import Response
from .serializers import ArticuloSerializer
from rest_framework import status
from rest_framework.decorators import api_view

@api_view(['GET','POST'])
def blog_api(request):
    if request.method=="GET":
        articulos=Articulo.objects.all()
        serializer=ArticuloSerializer(articulos,many=True)
        return Response(serializer.data)
    elif request.method=="POST":
        serializer=ArticuloSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def blog_api_detalle(request,pk):
    try:
        articulo=Articulo.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':
        serializer=ArticuloSerializer(articulo)
        return Response(serializer.data)
    elif request.method=="PUT":
        serializer=ArticuloSerializer(articulo,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.method=="DELETE":
        articulo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)