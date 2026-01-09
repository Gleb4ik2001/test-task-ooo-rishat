from typing import Any

from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления товарами.
    """

    list_display = (
        'id',
        'name',
        'price_display',
        'currency',
        'datetime_created'
    )
    list_filter = ('currency', 'datetime_created')
    search_fields = ('name', 'description')
    readonly_fields = ('datetime_created', 'datetime_updated')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'price', 'currency', 'image')
        }),
        ('Системная информация', {
            'fields': ('datetime_created', 'datetime_updated'),
            'classes': ('collapse',)
        }),
    )
