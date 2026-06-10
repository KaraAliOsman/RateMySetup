"""
Datos de demostracion para RateMySetup.

Crea usuarios, setups (con imagenes generadas), discos, calificaciones y
comentarios de ejemplo para ver la app con contenido.

Uso:
    python seed_demo.py

Para borrar todo y empezar de cero puedes usar:  python manage.py flush
"""
import os
from io import BytesIO

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratemysetup_project.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.core.files.base import ContentFile  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from core.models import Calificacion, Comentario, Disco, Setup  # noqa: E402


def generar_imagen(titulo, subtitulo, color):
    """Crea una imagen oscura con texto neon, para usar como foto del setup."""
    w, h = 1200, 675
    img = Image.new('RGB', (w, h), '#0d0f13')
    draw = ImageDraw.Draw(img)
    # Borde neon
    draw.rectangle([8, 8, w - 8, h - 8], outline=color, width=3)
    try:
        f_big = ImageFont.load_default(size=86)
        f_small = ImageFont.load_default(size=34)
    except TypeError:
        # Pillow viejo: load_default no acepta size
        f_big = ImageFont.load_default()
        f_small = ImageFont.load_default()

    def centrar(texto, font, y, fill):
        caja = draw.textbbox((0, 0), texto, font=font)
        tw = caja[2] - caja[0]
        draw.text(((w - tw) / 2, y), texto, font=font, fill=fill)

    centrar(titulo, f_big, h / 2 - 80, color)
    centrar(subtitulo, f_small, h / 2 + 40, '#9aa3b0')

    buffer = BytesIO()
    img.save(buffer, 'PNG')
    return ContentFile(buffer.getvalue())


def usuario(nombre):
    u, creado = User.objects.get_or_create(
        username=nombre, defaults={'email': f'{nombre}@demo.com'}
    )
    if creado:
        u.set_password('demo12345')
        u.save()
    return u


def crear_setup(autor, titulo, categoria, color, specs, discos):
    if Setup.objects.filter(titulo=titulo).exists():
        return Setup.objects.get(titulo=titulo)
    setup = Setup(usuario=autor, titulo=titulo, categoria=categoria, **specs)
    setup.imagen.save(
        f'{titulo.lower().replace(" ", "_")}.png',
        generar_imagen(titulo, f'{categoria.upper()}  -  RateMySetup', color),
        save=False,
    )
    setup.save()
    for tipo, tamano in discos:
        Disco.objects.create(setup=setup, tipo=tipo, tamano=tamano)
    return setup


def run():
    ana = usuario('ana')
    luis = usuario('luis')
    sofia = usuario('sofia')

    s1 = crear_setup(
        ana, 'Battlestation Gamer', 'gamer', '#39ff14',
        dict(
            descripcion='Setup principal para juegos AAA y streaming. RGB por todos lados.',
            ram_tamano='32GB', ram_frecuencia='3600MHz',
            cpu_marca='AMD Ryzen 7 5800X', cpu_socket='AM4',
            cpu_frecuencia='3.8GHz', cpu_nucleos=8,
            gpu_marca='NVIDIA RTX 4070', gpu_frecuencia='2.48GHz', gpu_vram='12GB',
        ),
        [('NVMe', '1TB'), ('SSD', '2TB'), ('HDD', '4TB')],
    )
    s2 = crear_setup(
        luis, 'Setup Minimalista', 'minimalista', '#00e5ff',
        dict(
            descripcion='Escritorio limpio, blanco y sin cables a la vista.',
            ram_tamano='16GB', ram_frecuencia='3200MHz',
            cpu_marca='Intel Core i5-12400', cpu_socket='LGA1700',
            cpu_frecuencia='2.5GHz', cpu_nucleos=6,
            gpu_marca='NVIDIA RTX 3060', gpu_frecuencia='1.78GHz', gpu_vram='12GB',
        ),
        [('NVMe', '500GB'), ('SSD', '1TB')],
    )
    s3 = crear_setup(
        sofia, 'Workstation Pro', 'workstation', '#b388ff',
        dict(
            descripcion='Para edicion de video y render 3D. Muchos nucleos y RAM.',
            ram_tamano='64GB', ram_frecuencia='3200MHz',
            cpu_marca='AMD Ryzen 9 5950X', cpu_socket='AM4',
            cpu_frecuencia='3.4GHz', cpu_nucleos=16,
            gpu_marca='NVIDIA RTX 4080', gpu_frecuencia='2.51GHz', gpu_vram='16GB',
        ),
        [('NVMe', '2TB'), ('SSD', '4TB')],
    )

    # Calificaciones (nadie vota su propio setup)
    pares = [
        (s1, luis, 5), (s1, sofia, 4),
        (s2, ana, 4), (s2, sofia, 5),
        (s3, ana, 5), (s3, luis, 5),
    ]
    for setup, user, puntaje in pares:
        Calificacion.objects.update_or_create(
            setup=setup, usuario=user, defaults={'puntaje': puntaje}
        )

    # Comentarios
    coments = [
        (s1, luis, 'Brutal el RGB, se ve increible.'),
        (s1, sofia, 'Que monitor usas? Se ve enorme.'),
        (s2, ana, 'Me encanta lo limpio que esta. Cero cables.'),
        (s3, luis, 'Esa CPU es un monstruo para render.'),
    ]
    for setup, user, texto in coments:
        if not Comentario.objects.filter(setup=setup, usuario=user, texto=texto).exists():
            Comentario.objects.create(setup=setup, usuario=user, texto=texto)

    print('Datos de demostracion creados.')
    print('Usuarios: ana / luis / sofia  (contrasena: demo12345)')
    print(f'Setups: {Setup.objects.count()} | Calificaciones: {Calificacion.objects.count()} | Comentarios: {Comentario.objects.count()}')


if __name__ == '__main__':
    run()
