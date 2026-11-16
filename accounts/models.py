from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    """Дополнительная информация о пользователе."""

    MAX_ABOUT_LENGTH = 5000

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )
    about = models.TextField(
        'О себе',
        max_length=MAX_ABOUT_LENGTH,
        blank=True,
        default='',
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


class Order(models.Model):
    """Заказ на бирже фриланса."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь',
    )
    url = models.URLField('URL заказа', max_length=2000)
    text = models.TextField('Текст заказа')
    customer_url = models.URLField(
        'URL профиля заказчика',
        max_length=2000,
        blank=True,
    )
    prospects_score = models.PositiveSmallIntegerField(
        'Оценка перспектив выполнить заказ',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Значение от 0 до 100.',
    )
    estimated_time = models.CharField(
        'Оценка времени выполнения',
        max_length=255,
        blank=True,
    )
    estimated_cost = models.CharField(
        'Оценка стоимости',
        max_length=255,
        blank=True,
    )
    response_text = models.TextField('Текст отклика', blank=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return self.url
