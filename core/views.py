from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Setup
from .forms import RegistroForm, SetupForm


def home(request):
    setups = Setup.objects.select_related('usuario').all()
    return render(request, 'core/home.html', {'setups': setups})


@login_required
def perfil(request):
    mis_setups = Setup.objects.filter(usuario=request.user)
    form = SetupForm()

    if request.method == 'POST':
        form = SetupForm(request.POST)
        if form.is_valid():
            setup = form.save(commit=False)
            setup.usuario = request.user
            setup.save()
            messages.success(request, '¡Setup publicado correctamente!')
            return redirect('perfil')

    return render(request, 'core/perfil.html', {'mis_setups': mis_setups, 'form': form})


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegistroForm()
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}! Tu cuenta ha sido creada.')
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
            messages.success(request, f'¡Bienvenido de vuelta, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('home')
