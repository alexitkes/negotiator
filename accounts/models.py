from django.conf import settings
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
