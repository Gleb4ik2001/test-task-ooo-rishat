"""Конфигурация приложения abstracts."""
from django.apps import AppConfig


class AbstractsConfig(AppConfig):
    """
    Конфигурация приложения abstracts.

    Это приложение содержит абстрактные модели,
    используемые другими приложениями проекта.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'abstracts'
    verbose_name = 'Абстрактные модели'
