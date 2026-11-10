from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def home(request):
    """Домашняя страница вошедшего пользователя."""
    return render(request, 'home.html')


def logout_view(request):
    """Выход пользователя из системы."""
    logout(request)
    return redirect('login')
