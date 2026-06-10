from django.contrib import admin

from .models import Calificacion, Comentario, Disco, Setup


class DiscoInline(admin.TabularInline):
    model = Disco
    extra = 1


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('usuario', 'texto', 'fecha_creacion')


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'categoria', 'promedio_calificacion', 'fecha_creacion')
    list_filter = ('categoria', 'usuario')
    search_fields = ('titulo', 'descripcion', 'cpu_marca', 'gpu_marca')
    inlines = [DiscoInline, ComentarioInline]


@admin.register(Disco)
class DiscoAdmin(admin.ModelAdmin):
    list_display = ('setup', 'tipo', 'tamano')
    list_filter = ('tipo',)


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('setup', 'usuario', 'puntaje', 'fecha')
    list_filter = ('puntaje',)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('setup', 'usuario', 'fecha_creacion')
    search_fields = ('texto',)
