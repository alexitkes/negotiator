from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm
from .models import Profile


@login_required
def home(request):
    """Домашняя страница вошедшего пользователя с редактированием информации о себе."""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация о себе сохранена.')
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'home.html', {'form': form})


def logout_view(request):
    """Выход пользователя из системы."""
    logout(request)
    return redirect('login')
