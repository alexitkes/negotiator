from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Order, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профиль'
    fields = ('about',)


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'prospects_score', 'estimated_time', 'estimated_cost', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('url', 'text', 'customer_url', 'response_text')
    readonly_fields = ('created_at',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
