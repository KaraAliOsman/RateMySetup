import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Calificacion, Comentario, Disco, Setup


def imagen_de_prueba(nombre='test.png'):
    """Genera una imagen PNG valida en memoria para los tests de subida."""
    buffer = BytesIO()
    Image.new('RGB', (12, 12), 'green').save(buffer, 'PNG')
    buffer.seek(0)
    return SimpleUploadedFile(nombre, buffer.read(), content_type='image/png')


def datos_setup(**extra):
    """POST base para publicar un setup (incluye el management form del formset)."""
    data = {
        'titulo': 'PC Gamer de prueba',
        'categoria': 'gamer',
        'descripcion': 'Setup de prueba',
        'ram_tamano': '16GB', 'ram_frecuencia': '3200MHz',
        'cpu_marca': 'Ryzen 5 5600X', 'cpu_socket': 'AM4',
        'cpu_frecuencia': '3.7GHz', 'cpu_nucleos': '6',
        'gpu_marca': 'RTX 3060', 'gpu_frecuencia': '1.78GHz', 'gpu_vram': '12GB',
        # Formset de discos (prefijo 'discos' por el related_name)
        'discos-TOTAL_FORMS': '2',
        'discos-INITIAL_FORMS': '0',
        'discos-MIN_NUM_FORMS': '0',
        'discos-MAX_NUM_FORMS': '1000',
        'discos-0-tipo': 'NVMe', 'discos-0-tamano': '1TB', 'discos-0-id': '',
        'discos-1-tipo': 'SSD', 'discos-1-tamano': '', 'discos-1-id': '',  # vacio -> se ignora
    }
    data.update(extra)
    return data


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RateMySetupTests(TestCase):
    def setUp(self):
        self.autor = User.objects.create_user('autor', password='clave12345')
        self.visitante = User.objects.create_user('visitante', password='clave12345')

    # ---------- Paginas publicas ----------
    def test_home_responde(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_home_filtra_por_categoria(self):
        self._crear_setup_directo(categoria='gamer', titulo='Uno')
        self._crear_setup_directo(categoria='oficina', titulo='Dos')
        resp = self.client.get(reverse('home'), {'categoria': 'oficina'})
        self.assertContains(resp, 'Dos')
        self.assertNotContains(resp, 'Uno')

    # ---------- Crear setup con imagen + discos ----------
    def test_crear_setup_con_imagen_y_discos(self):
        self.client.force_login(self.autor)
        data = datos_setup(imagen=imagen_de_prueba())
        resp = self.client.post(reverse('setup_nuevo'), data)
        self.assertEqual(resp.status_code, 302)  # redirige al detalle
        setup = Setup.objects.get(titulo='PC Gamer de prueba')
        self.assertEqual(setup.usuario, self.autor)
        self.assertEqual(setup.cpu_nucleos, 6)
        self.assertTrue(setup.imagen.name.endswith('.png'))
        # Solo se guardo 1 disco (la 2da fila estaba vacia)
        self.assertEqual(setup.discos.count(), 1)
        self.assertEqual(setup.discos.first().tipo, 'NVMe')

    def test_detalle_muestra_specs(self):
        setup = self._crear_setup_directo()
        Disco.objects.create(setup=setup, tipo='SSD', tamano='500GB')
        resp = self.client.get(reverse('setup_detalle', args=[setup.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ryzen')
        self.assertContains(resp, '500GB')

    # ---------- Calificaciones (reglas del profesor) ----------
    def test_no_puede_votar_su_propio_setup(self):
        setup = self._crear_setup_directo()
        self.client.force_login(self.autor)
        self.client.post(reverse('calificar', args=[setup.pk]), {'puntaje': '5'})
        self.assertEqual(setup.calificaciones.count(), 0)

    def test_no_puede_votar_dos_veces(self):
        setup = self._crear_setup_directo()
        self.client.force_login(self.visitante)
        self.client.post(reverse('calificar', args=[setup.pk]), {'puntaje': '4'})
        self.client.post(reverse('calificar', args=[setup.pk]), {'puntaje': '2'})
        # Sigue habiendo un solo voto, pero actualizado a 2
        self.assertEqual(setup.calificaciones.count(), 1)
        self.assertEqual(setup.calificaciones.first().puntaje, 2)

    def test_promedio_se_calcula(self):
        setup = self._crear_setup_directo()
        otro = User.objects.create_user('otro', password='clave12345')
        Calificacion.objects.create(setup=setup, usuario=self.visitante, puntaje=4)
        Calificacion.objects.create(setup=setup, usuario=otro, puntaje=2)
        self.assertEqual(setup.promedio_calificacion(), 3.0)

    def test_puntaje_invalido_se_rechaza(self):
        setup = self._crear_setup_directo()
        self.client.force_login(self.visitante)
        self.client.post(reverse('calificar', args=[setup.pk]), {'puntaje': '9'})
        self.assertEqual(setup.calificaciones.count(), 0)

    # ---------- Comentarios ----------
    def test_usuario_logueado_comenta(self):
        setup = self._crear_setup_directo()
        self.client.force_login(self.visitante)
        self.client.post(reverse('comentar', args=[setup.pk]), {'texto': 'Que buen setup!'})
        self.assertEqual(setup.comentarios.count(), 1)
        self.assertEqual(setup.comentarios.first().usuario, self.visitante)

    # ---------- Permisos ----------
    def test_solo_el_dueno_edita(self):
        setup = self._crear_setup_directo()
        self.client.force_login(self.visitante)  # no es el dueno
        resp = self.client.get(reverse('setup_editar', args=[setup.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_dueno_elimina_su_setup(self):
        setup = self._crear_setup_directo()
        self.client.force_login(self.autor)
        resp = self.client.post(reverse('setup_eliminar', args=[setup.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Setup.objects.filter(pk=setup.pk).exists())

    # ---------- Helper ----------
    def _crear_setup_directo(self, **extra):
        campos = dict(
            usuario=self.autor, titulo='PC del autor', categoria='gamer',
            cpu_marca='Ryzen 5 5600X', imagen=imagen_de_prueba(),
        )
        campos.update(extra)
        return Setup.objects.create(**campos)
