from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import Comentario, Disco, Setup


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electronico")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SetupForm(forms.ModelForm):
    """Formulario para publicar / editar un setup con todo su hardware."""

    class Meta:
        model = Setup
        fields = (
            'titulo', 'categoria', 'descripcion', 'imagen',
            'ram_tamano', 'ram_frecuencia',
            'cpu_marca', 'cpu_socket', 'cpu_frecuencia', 'cpu_nucleos',
            'gpu_marca', 'gpu_frecuencia', 'gpu_vram',
        )
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica clases de Bootstrap a cada campo automaticamente.
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault('class', 'form-control')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            else:
                widget.attrs.setdefault('class', 'form-control')
            # Usa el help_text del modelo como placeholder cuando exista.
            if field.help_text and not widget.attrs.get('placeholder'):
                widget.attrs['placeholder'] = field.help_text


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('texto',)
        labels = {'texto': ''}
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Escribe tu opinion sobre este setup...',
            }),
        }


# Formset en linea: permite agregar varios discos a un mismo setup.
# extra=2 -> muestra 2 filas vacias; can_delete=True -> permite quitar discos al editar.
DiscoFormSet = inlineformset_factory(
    Setup,
    Disco,
    fields=('tipo', 'tamano'),
    extra=2,
    can_delete=True,
    widgets={
        'tipo': forms.Select(attrs={'class': 'form-select'}),
        'tamano': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 1TB, 500GB',
        }),
    },
)
