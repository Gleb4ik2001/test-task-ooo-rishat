"""Модели для работы с заказами, скидками и налогами."""
from typing import TYPE_CHECKING

from django.core.validators import MaxValueValidator
from django.db import models

from abstracts.models import TimeStampModel

if TYPE_CHECKING:
    from items.models import Item


class Order(TimeStampModel):
    """
    Модель заказа.

    Представляет заказ, который может содержать несколько товаров,
    скидку и налог.

    Attributes:
        is_paid: Статус оплаты заказа
        discount: Примененная скидка (опционально)
        tax: Примененный налог (опционально)
        datetime_created: Дата и время создания
        datetime_updated: Дата и время обновления

    Methods:
        subtotal: Возвращает промежуточную сумму без скидок и налогов
        total_amount: Возвращает итоговую сумму с учетом скидок и налогов
    """

    is_paid = models.BooleanField(
        verbose_name='статус оплаты',
        default=False
    )

    discount = models.ForeignKey(
        verbose_name='скидка',
        to='Discount',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    tax = models.ForeignKey(
        verbose_name='налог',
        to='Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def subtotal(self) -> int:
        """
        Вычисляет промежуточную сумму заказа без учета скидок и налогов.

        Returns:
            Промежуточная сумма в центах
        """
        return sum(
            i.item.price * i.quantity for i in self.items.all()
        )

    def total_amount(self) -> int:
        """
        Вычисляет итоговую сумму заказа с учетом скидок и налогов.

        Сначала применяется скидка, затем налог к сумме после скидки.

        Returns:
            Итоговая сумма в центах
        """
        total = self.subtotal()

        if self.discount:
            total = total * (100 - self.discount.percent) // 100

        if self.tax:
            total = total * (100 + self.tax.percent) // 100

        return int(total)

    class Meta:
        """Метаданные модели."""

        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-id',)


class OrderItem(models.Model):
    """
    Модель товара в заказе.

    Связывает заказ с товаром и указывает количество.

    Attributes:
        order: Заказ, к которому относится товар
        item: Товар
        quantity: Количество товара
    """

    order = models.ForeignKey(
        verbose_name='заказ',
        to=Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        verbose_name='товар',
        to='items.Item',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        default=1
    )

    def __str__(self) -> str:
        """
        Строковое представление товара в заказе.

        Returns:
            Строка с информацией о товаре и статусе оплаты
        """
        status = 'оплачен' if self.order.is_paid else 'не оплачен'
        return (
            f"Заказ: {self.item.name} в количестве - "
            f"{self.quantity} {status}"
        )

    class Meta:
        """Метаданные модели."""

        verbose_name = 'товар в заказе'
        verbose_name_plural = 'товары в заказах'
        ordering = ('-id',)


class Discount(TimeStampModel):
    """
    Модель скидки.

    Представляет скидку с промокодом и процентом скидки.

    Attributes:
        name: Название скидки
        code: Промокод для активации скидки (уникальный)
        percent: Процент скидки (0-100)
        datetime_created: Дата и время создания
        datetime_updated: Дата и время обновления
    """

    name = models.CharField(
        verbose_name='название',
        max_length=255
    )
    code = models.CharField(
        verbose_name="промокод",
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    percent = models.PositiveIntegerField(
        verbose_name='процент скидки',
        help_text="скидка в процентах",
        validators=[
            MaxValueValidator(
                100,
                'скидка не может быть больше 100'
            )
        ]
    )

    def __str__(self) -> str:
        """
        Строковое представление скидки.

        Returns:
            Строка с названием, кодом и процентом скидки
        """
        code_str = f" код: {self.code}" if self.code else ""
        return f"{self.name}{code_str} процент скидки: {self.percent}%"

    class Meta:
        """Метаданные модели."""

        verbose_name = 'скидка'
        verbose_name_plural = 'скидки'
        ordering = ('-percent',)


class Tax(TimeStampModel):
    """
    Модель налога.

    Представляет налог с названием и процентом.

    Attributes:
        name: Название налога
        percent: Процент налога (0-100)
        datetime_created: Дата и время создания
        datetime_updated: Дата и время обновления
    """

    name = models.CharField(
        verbose_name='название',
        max_length=255
    )
    percent = models.PositiveIntegerField(
        verbose_name='процент',
        help_text="налог в процентах",
        validators=[
            MaxValueValidator(
                100,
                'процент не может превышать значение 100'
            )
        ]
    )

    def __str__(self) -> str:
        """
        Строковое представление налога.

        Returns:
            Строка с названием и процентом налога
        """
        return f"{self.name} (+{self.percent}%)"

    class Meta:
        """Метаданные модели."""

        verbose_name = 'налог'
        verbose_name_plural = 'налоги'
        ordering = ('-percent',)
