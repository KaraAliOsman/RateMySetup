from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),

    # Setups
    path('setup/nuevo/', views.setup_nuevo, name='setup_nuevo'),
    path('setup/<int:pk>/', views.setup_detalle, name='setup_detalle'),
    path('setup/<int:pk>/editar/', views.setup_editar, name='setup_editar'),
    path('setup/<int:pk>/eliminar/', views.setup_eliminar, name='setup_eliminar'),
    path('setup/<int:pk>/calificar/', views.calificar, name='calificar'),
    path('setup/<int:pk>/comentar/', views.comentar, name='comentar'),

    # Cuenta
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
