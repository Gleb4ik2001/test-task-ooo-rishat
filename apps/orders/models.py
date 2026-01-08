from django.db import models
from items.models import Item
from abstracts.models import TimeStampModel

class Order(TimeStampModel):
    is_paid = models.BooleanField(default=False)

    def total_amount(self):
        return sum(i.item.price * i.quantity for i in self.items.all())


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
