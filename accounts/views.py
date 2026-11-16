import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import OrderForm, ProfileForm
from .models import Order, Profile
from .services import LLMError, generate_order_response


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


@login_required
def order_list(request):
    """Список заказов текущего пользователя."""
    orders = request.user.orders.all()
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_create(request):
    """Добавление нового заказа."""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, 'Заказ добавлен.')
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(
        request,
        'orders/order_form.html',
        {'form': form, 'form_action': reverse('order_create')},
    )


@login_required
def order_edit(request, pk):
    """Редактирование собственного заказа пользователя."""
    order = get_object_or_404(Order, pk=pk, user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ обновлён.')
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)

    return render(
        request,
        'orders/order_form.html',
        {'form': form, 'form_action': reverse('order_edit', args=[order.pk]), 'order': order},
    )


@login_required
@require_POST
def order_generate_response(request):
    """Генерирует отклик и оценки по заказу с помощью LLM."""
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный формат запроса.'}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({'error': 'Некорректный формат запроса.'}, status=400)

    order_text = (payload.get('text') or '').strip()
    customer_url = (payload.get('customer_url') or '').strip()

    if not order_text:
        return JsonResponse(
            {'error': 'Введите текст заказа, чтобы сгенерировать отклик.'},
            status=400,
        )

    profile, _ = Profile.objects.get_or_create(user=request.user)
    skills = (profile.about or '').strip()
    if not skills:
        return JsonResponse(
            {
                'error': 'Сначала заполните поле «О себе» на домашней странице: '
                'оно используется как описание навыков фрилансера.'
            },
            status=400,
        )

    try:
        result = generate_order_response(order_text, skills, customer_url)
    except LLMError as exc:
        return JsonResponse({'error': str(exc)}, status=502)

    return JsonResponse(result)


@login_required
@require_POST
def order_delete(request, pk):
    """Удаление собственного заказа пользователя."""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.delete()
    messages.success(request, 'Заказ удалён.')
    return redirect('order_list')


def logout_view(request):
    """Выход пользователя из системы."""
    logout(request)
    return redirect('login')
