from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import LLMCall, Order, Profile


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


@admin.register(LLMCall)
class LLMCallAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'order', 'model_name', 'prompt_tokens', 'completion_tokens', 'total_tokens')
    list_filter = ('model_name', 'created_at', 'user')
    search_fields = ('model_name', 'user__username', 'order__url')
    readonly_fields = (
        'user',
        'order',
        'model_name',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'created_at',
    )

    def has_add_permission(self, request):
        return False


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
