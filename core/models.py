from django.contrib.auth.models import User
from django.db import models


class Setup(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='setups')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    url_imagen = models.URLField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
