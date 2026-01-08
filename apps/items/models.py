from django.db import models

from abstracts.models import TimeStampModel

class Item(TimeStampModel):
    
    class CurrencyChoices(models.TextChoices):
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
    def price_display(self):
        return self.price / 100
    

    def __str__(self):
        return f'{self.name} - ${self.price_display:2f}'
    
    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ('-id',)