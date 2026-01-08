from django.db import models

class TimeStampModel(models.Model):
    datetime_created = models.DateTimeField(
        verbose_name='дата и время создания',
        auto_now_add=True
    )
    datetime_updated = models.DateTimeField(
        verbose_name='дата и время редактирования',
        auto_now=True
    )

    class Meta:
        abstract = True