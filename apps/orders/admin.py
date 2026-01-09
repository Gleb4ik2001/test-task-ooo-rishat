from typing import Any, Optional

from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem, Discount, Tax


class OrderItemInline(admin.TabularInline):
    """
    Inline админ для отображения товаров заказа.

    Позволяет редактировать товары заказа прямо на странице заказа.
    """

    model = OrderItem
    extra = 0
    fields = ('item', 'quantity', 'get_item_price', 'get_total')
    readonly_fields = ('get_item_price', 'get_total')

    def get_item_price(self, obj: OrderItem) -> str:
        """
        Возвращает цену товара с валютой.

        Args:
            obj: Объект OrderItem

        Returns:
            Строка с ценой и валютой или "-" если товар отсутствует
        """
        if obj.item:
            return (
                f"{obj.item.price_display:.2f} "
                f"{obj.item.currency.upper()}"
            )
        return "-"

    get_item_price.short_description = 'Цена товара'

    def get_total(self, obj: OrderItem) -> str:
        """
        Возвращает общую стоимость товара (цена * количество).

        Args:
            obj: Объект OrderItem

        Returns:
            Строка с общей стоимостью и валютой или "-" если товар отсутствует
        """
        if obj.item:
            total = obj.item.price * obj.quantity / 100
            return f"{total:.2f} {obj.item.currency.upper()}"
        return "-"

    get_total.short_description = 'Итого'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления заказами.

    Отображает информацию о заказе, включая количество товаров,
    промежуточную и итоговую суммы с учетом скидок и налогов.
    """

    list_display = (
        'id',
        'get_items_count',
        'get_subtotal',
        'get_total',
        'is_paid',
        'datetime_created'
    )
    list_filter = ('is_paid', 'datetime_created', 'discount', 'tax')
    search_fields = ('id',)
    readonly_fields = (
        'datetime_created',
        'datetime_updated',
        'get_subtotal',
        'get_total'
    )
    inlines = [OrderItemInline]
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('is_paid', 'discount', 'tax')
        }),
        ('Расчеты', {
            'fields': ('get_subtotal', 'get_total'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('datetime_created', 'datetime_updated'),
            'classes': ('collapse',)
        }),
    )

    def get_items_count(self, obj: Order) -> int:
        """
        Возвращает количество товаров в заказе.

        Args:
            obj: Объект Order

        Returns:
            Количество товаров в заказе
        """
        return obj.items.count()

    get_items_count.short_description = 'Количество товаров'

    def get_subtotal(self, obj: Order) -> str:
        """
        Возвращает промежуточную сумму заказа без учета скидок и налогов.

        Args:
            obj: Объект Order

        Returns:
            Строка с промежуточной суммой и валютой
        """
        subtotal = obj.subtotal() / 100
        if obj.items.exists():
            currency = obj.items.first().item.currency.upper()
            return f"{subtotal:.2f} {currency}"
        return "0.00"

    get_subtotal.short_description = 'Промежуточная сумма'

    def get_total(self, obj: Order) -> str:
        """
        Возвращает итоговую сумму заказа с учетом скидок и налогов.

        Args:
            obj: Объект Order

        Returns:
            Строка с итоговой суммой и валютой
        """
        total = obj.total_amount() / 100
        if obj.items.exists():
            currency = obj.items.first().item.currency.upper()
            return f"{total:.2f} {currency}"
        return "0.00"

    get_total.short_description = 'Итоговая сумма'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления товарами в заказах.

    Позволяет просматривать и редактировать отдельные товары в заказах.
    """

    list_display = ('id', 'order', 'item', 'quantity', 'get_total')
    list_filter = ('order', 'item')
    search_fields = ('order__id', 'item__name')

    def get_total(self, obj: OrderItem) -> str:
        """
        Возвращает общую стоимость товара (цена * количество).

        Args:
            obj: Объект OrderItem

        Returns:
            Строка с общей стоимостью и валютой или "-" если товар отсутствует
        """
        if obj.item:
            total = obj.item.price * obj.quantity / 100
            return f"{total:.2f} {obj.item.currency.upper()}"
        return "-"

    get_total.short_description = 'Итого'


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления скидками.

    Позволяет создавать и управлять скидками с промокодами.
    """

    list_display = (
        'id',
        'name',
        'code',
        'percent',
        'datetime_created'
    )
    list_filter = ('percent', 'datetime_created')
    search_fields = ('name', 'code')
    readonly_fields = ('datetime_created', 'datetime_updated')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'code', 'percent')
        }),
        ('Системная информация', {
            'fields': ('datetime_created', 'datetime_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления налогами.

    Позволяет создавать и управлять налогами для заказов.
    """

    list_display = ('id', 'name', 'percent', 'datetime_created')
    list_filter = ('percent', 'datetime_created')
    search_fields = ('name',)
    readonly_fields = ('datetime_created', 'datetime_updated')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'percent')
        }),
        ('Системная информация', {
            'fields': ('datetime_created', 'datetime_updated'),
            'classes': ('collapse',)
        }),
    )
