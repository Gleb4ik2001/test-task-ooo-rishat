"""Абстрактные модели для проекта."""
from django.db import models


class TimeStampModel(models.Model):
    """
    Абстрактная модель с полями для отслеживания времени создания и обновления.

    Эта модель добавляет автоматические поля datetime_created и datetime_updated
    ко всем моделям, которые от нее наследуются.

    Attributes:
        datetime_created: Дата и время создания записи (автоматически)
        datetime_updated: Дата и время последнего обновления (автоматически)
    """

    datetime_created = models.DateTimeField(
        verbose_name='дата и время создания',
        auto_now_add=True
    )
    datetime_updated = models.DateTimeField(
        verbose_name='дата и время редактирования',
        auto_now=True
    )

    class Meta:
        """Метаданные модели."""

        abstract = True
