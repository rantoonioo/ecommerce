##forms articulo
from django import forms
from .models import Articulo

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['titulo','descripcion', 'imagen','precio','stock']  # Agregar 'imagen'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),  # Agregar widget para imagen
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),  # Campo descripción
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),  # Campo precio
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),  # Widget para el campo 'stock'
          
            
        }
