from django.db import models
from items.models import Item
from abstracts.models import TimeStampModel
from django.core.validators import MaxValueValidator

class Order(TimeStampModel):
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
    
    def subtotal(self):
        return sum(i.item.price * i.quantity for i in self.items.all())

    def total_amount(self):
        total = self.subtotal()

        if self.discount:
            total = total * (100 - self.discount.percent) // 100
            
        if self.tax:
            total = total * (100 + self.tax.percent) // 100

        return int(total)


class OrderItem(models.Model):
    order = models.ForeignKey(
        verbose_name='заказ',
        to=Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        verbose_name='товар',
        to=Item,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        default=1
    )

    def __str__(self) -> str:
        return f"Заказ: {self.item.name} в количестве - {self.quantity} {'оплачен' if self.order.is_paid else 'не оплачен'}"
    
    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-id',)


class Discount(TimeStampModel):
    name = models.CharField(
        verbose_name='название',
        max_length=255
    )
    code = models.CharField(
        verbose_name="промокод",
        max_length=50,
        unique=True,
        null=True
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

    def __str__(self):
        return f"{self.name} код: {self.code} процент скидки: {self.percent}%)"
    
    class Meta:
        verbose_name = 'скидка'
        verbose_name_plural = 'скидки'
        ordering = ('-percent',)


class Tax(TimeStampModel):
    name = models.CharField(max_length=255)
    percent = models.PositiveIntegerField(
        verbose_name='процент',
        help_text="налог в процентах",
        validators=[
            MaxValueValidator(100, 'процент не может превышать значение 100')
        ]
    )

    def __str__(self):
        return f"{self.name} (+{self.percent}%)"
    
    class Meta:
        verbose_name = 'налог'
        verbose_name_plural = 'налоги'
        ordering = ('-percent',)