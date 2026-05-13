from django.contrib import admin
from .models import Setup


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'fecha_creacion')
    list_filter = ('usuario',)
    search_fields = ('titulo', 'descripcion')
