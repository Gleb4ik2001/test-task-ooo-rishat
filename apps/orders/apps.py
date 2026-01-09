from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Конфигурация приложения orders.

    Это приложение содержит модели и views для работы с заказами,
    корзиной, скидками и налогами.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Заказы'
