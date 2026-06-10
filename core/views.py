from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ComentarioForm, DiscoFormSet, RegistroForm, SetupForm
from .models import Calificacion, Setup


def home(request):
    """Inicio: lista de setups con filtro opcional por categoria."""
    categoria = request.GET.get('categoria', '')
    setups = Setup.objects.select_related('usuario').prefetch_related('calificaciones')
    if categoria:
        setups = setups.filter(categoria=categoria)

    return render(request, 'core/home.html', {
        'setups': setups,
        'categoria_actual': categoria,
        'categorias': Setup.CATEGORIA_CHOICES,
    })


@login_required
def perfil(request):
    """Panel del usuario: lista de sus propios setups."""
    mis_setups = Setup.objects.filter(usuario=request.user).prefetch_related('calificaciones')
    return render(request, 'core/perfil.html', {'mis_setups': mis_setups})


@login_required
def setup_nuevo(request):
    """Publicar un setup nuevo, junto con sus discos (formset)."""
    if request.method == 'POST':
        form = SetupForm(request.POST, request.FILES)
        formset = DiscoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            setup = form.save(commit=False)
            setup.usuario = request.user
            setup.save()
            formset.instance = setup
            formset.save()
            messages.success(request, 'Setup publicado correctamente.')
            return redirect('setup_detalle', pk=setup.pk)
    else:
        form = SetupForm()
        formset = DiscoFormSet()

    return render(request, 'core/setup_form.html', {
        'form': form,
        'formset': formset,
        'modo': 'nuevo',
    })


@login_required
def setup_editar(request, pk):
    """Editar un setup. Solo el dueno puede hacerlo."""
    setup = get_object_or_404(Setup, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = SetupForm(request.POST, request.FILES, instance=setup)
        formset = DiscoFormSet(request.POST, instance=setup)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Setup actualizado correctamente.')
            return redirect('setup_detalle', pk=setup.pk)
    else:
        form = SetupForm(instance=setup)
        formset = DiscoFormSet(instance=setup)

    return render(request, 'core/setup_form.html', {
        'form': form,
        'formset': formset,
        'modo': 'editar',
        'setup': setup,
    })


@login_required
def setup_eliminar(request, pk):
    """Eliminar un setup. Solo el dueno puede hacerlo."""
    setup = get_object_or_404(Setup, pk=pk, usuario=request.user)
    if request.method == 'POST':
        setup.delete()
        messages.info(request, 'Setup eliminado.')
        return redirect('perfil')
    return render(request, 'core/setup_eliminar.html', {'setup': setup})


def setup_detalle(request, pk):
    """Detalle publico: hardware completo, calificaciones y comentarios."""
    setup = get_object_or_404(
        Setup.objects
        .select_related('usuario')
        .prefetch_related('discos', 'comentarios__usuario'),
        pk=pk,
    )

    mi_voto = None
    if request.user.is_authenticated:
        voto = setup.calificaciones.filter(usuario=request.user).first()
        mi_voto = voto.puntaje if voto else None

    return render(request, 'core/setup_detalle.html', {
        'setup': setup,
        'comentario_form': ComentarioForm(),
        'mi_voto': mi_voto,
        'es_dueno': request.user == setup.usuario,
        'rango_estrellas': [5, 4, 3, 2, 1],  # orden inverso para el truco CSS de estrellas
    })


@login_required
def calificar(request, pk):
    """Registra el voto (1-5) del usuario. No puede votar su propio setup."""
    setup = get_object_or_404(Setup, pk=pk)

    if request.method != 'POST':
        return redirect('setup_detalle', pk=pk)

    if setup.usuario == request.user:
        messages.error(request, 'No puedes calificar tu propio setup.')
        return redirect('setup_detalle', pk=pk)

    try:
        puntaje = int(request.POST.get('puntaje', 0))
    except (TypeError, ValueError):
        puntaje = 0

    if not 1 <= puntaje <= 5:
        messages.error(request, 'Selecciona una calificacion valida (1 a 5 estrellas).')
        return redirect('setup_detalle', pk=pk)

    # update_or_create: si ya voto, actualiza su voto; si no, lo crea.
    # El unique_together del modelo garantiza que no haya votos duplicados.
    Calificacion.objects.update_or_create(
        setup=setup,
        usuario=request.user,
        defaults={'puntaje': puntaje},
    )
    messages.success(request, f'Calificaste este setup con {puntaje} estrella{"s" if puntaje != 1 else ""}.')
    return redirect('setup_detalle', pk=pk)


@login_required
def comentar(request, pk):
    """Agrega un comentario al setup."""
    setup = get_object_or_404(Setup, pk=pk)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.setup = setup
            comentario.usuario = request.user
            comentario.save()
            messages.success(request, 'Comentario publicado.')
        else:
            messages.error(request, 'Tu comentario no puede estar vacio.')
    return redirect('setup_detalle', pk=pk)


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegistroForm()
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}. Tu cuenta fue creada.')
            return redirect('perfil')

    return render(request, 'core/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido de vuelta, {user.username}.')
            return redirect(request.GET.get('next', 'home'))

        messages.error(request, 'Usuario o contrasena incorrectos.')

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesion correctamente.')
    return redirect('home')
