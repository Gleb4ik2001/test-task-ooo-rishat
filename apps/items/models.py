"""Модели для работы с товарами."""
from django.db import models

from abstracts.models import TimeStampModel


class Item(TimeStampModel):
    """
    Модель товара.

    Представляет товар в магазине с информацией о названии,
    описании, цене, валюте и изображении.

    Attributes:
        name: Название товара
        description: Описание товара
        price: Цена товара в центах (для точности расчетов)
        currency: Валюта товара (USD или KZT)
        image: Изображение товара (опционально)
        datetime_created: Дата и время создания
        datetime_updated: Дата и время обновления

    Properties:
        price_display: Возвращает цену сразу в долларах (не в центах)
    """

    class CurrencyChoices(models.TextChoices):
        """Выбор валюты для товара."""

        USD = "usd", "USD"
        KZT = "kzt", "KZT"

    name = models.CharField(
        verbose_name='название',
        max_length=255
    )
    description = models.TextField(verbose_name='описание')
    price = models.IntegerField(verbose_name='цена в центах')
    currency = models.CharField(
        verbose_name="валюта",
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD
    )
    image = models.ImageField(
        verbose_name="изображение",
        upload_to="items/",
        blank=True,
        null=True
    )

    @property
    def price_display(self) -> float:
        """
        Возвращает цену товара в обычном формате.

        Конвертирует цену из центов в обычные единицы валюты.

        Returns:
            Цена товара в обычном формате (не в центах)
        """
        return self.price / 100

    def __str__(self) -> str:
        return f'{self.name} - ${self.price_display:.2f}'

    class Meta:
        """Метаданные модели."""

        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ('-id',)
