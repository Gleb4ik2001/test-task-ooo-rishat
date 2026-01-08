from django.db import models

from abstracts.models import TimeStampModel

class Item(TimeStampModel):
    name = models.CharField(verbose_name='название', max_length=255)
    description = models.TextField(verbose_name='описание')
    price = models.IntegerField(verbose_name='цена в центах')
    

    @property
    def price_display(self):
        return self.price / 100
    

    def __str__(self):
        return f'{self.name} - ${self.price_display:2f}'
    
    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ('-id',)