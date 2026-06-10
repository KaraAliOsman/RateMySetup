from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class Setup(models.Model):
    """Publicacion principal: un escritorio/PC con su hardware en detalle."""

    # --- Categorias para filtrar en el inicio ---
    CATEGORIA_CHOICES = [
        ('gamer', 'Gamer'),
        ('oficina', 'Oficina'),
        ('minimalista', 'Minimalista'),
        ('streaming', 'Streaming'),
        ('workstation', 'Workstation'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='setups')
    titulo = models.CharField('Titulo', max_length=200)
    descripcion = models.TextField('Descripcion', blank=True)
    # Antes era una URL; ahora el usuario sube la foto desde su PC.
    imagen = models.ImageField('Imagen', upload_to='setups/')
    categoria = models.CharField(
        'Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='gamer'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # --- RAM ---
    ram_tamano = models.CharField(
        'RAM - Tamano', max_length=30, blank=True, help_text='Ej: 16GB, 32GB'
    )
    ram_frecuencia = models.CharField(
        'RAM - Frecuencia', max_length=30, blank=True, help_text='Ej: 3200MHz'
    )

    # --- CPU ---
    cpu_marca = models.CharField(
        'CPU - Marca / Modelo', max_length=80, blank=True,
        help_text='Ej: AMD Ryzen 5 5600X',
    )
    cpu_socket = models.CharField(
        'CPU - Socket', max_length=30, blank=True, help_text='Ej: AM4, LGA1700'
    )
    cpu_frecuencia = models.CharField(
        'CPU - Frecuencia', max_length=30, blank=True, help_text='Ej: 3.7GHz'
    )
    cpu_nucleos = models.PositiveIntegerField(
        'CPU - Nucleos', null=True, blank=True, help_text='Ej: 6'
    )

    # --- GPU ---
    gpu_marca = models.CharField(
        'GPU - Marca / Modelo', max_length=80, blank=True,
        help_text='Ej: NVIDIA RTX 3060',
    )
    gpu_frecuencia = models.CharField(
        'GPU - Frecuencia', max_length=30, blank=True, help_text='Ej: 1.78GHz'
    )
    gpu_vram = models.CharField(
        'GPU - VRAM', max_length=30, blank=True, help_text='Ej: 12GB'
    )

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

    # --- Helpers de calificacion (se usan en los templates) ---
    def promedio_calificacion(self):
        """Promedio de estrellas (0 si todavia no tiene votos)."""
        return self.calificaciones.aggregate(prom=Avg('puntaje'))['prom'] or 0

    def promedio_redondeado(self):
        """Promedio redondeado al entero mas cercano, para pintar estrellas."""
        return round(self.promedio_calificacion())

    def total_calificaciones(self):
        return self.calificaciones.count()


class Disco(models.Model):
    """Un setup puede tener varios discos (relacion uno-a-muchos)."""

    TIPO_CHOICES = [
        ('HDD', 'HDD'),
        ('SSD', 'SSD'),
        ('NVMe', 'NVMe'),
    ]

    setup = models.ForeignKey(Setup, on_delete=models.CASCADE, related_name='discos')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES, default='SSD')
    tamano = models.CharField('Tamano', max_length=30, help_text='Ej: 1TB, 500GB')

    def __str__(self):
        return f"{self.tipo} {self.tamano}"


class Calificacion(models.Model):
    """Voto de 1 a 5 estrellas. Un usuario solo puede votar una vez por setup."""

    setup = models.ForeignKey(
        Setup, on_delete=models.CASCADE, related_name='calificaciones'
    )
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='calificaciones'
    )
    puntaje = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    fecha = models.DateTimeField(auto_now=True)

    class Meta:
        # Impide que el mismo usuario vote dos veces el mismo setup.
        unique_together = ('setup', 'usuario')

    def __str__(self):
        return f"{self.usuario.username} -> {self.setup.titulo}: {self.puntaje}*"


class Comentario(models.Model):
    """Opinion de un usuario en un setup."""

    setup = models.ForeignKey(
        Setup, on_delete=models.CASCADE, related_name='comentarios'
    )
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comentarios'
    )
    texto = models.TextField('Comentario')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username} en {self.setup.titulo}"
