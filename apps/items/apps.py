from django.apps import AppConfig


class ItemsConfig(AppConfig):
    """
    Конфигурация приложения items.

    Это приложение содержит модели и views для работы с товарами.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'items'
    verbose_name = 'Товары'
