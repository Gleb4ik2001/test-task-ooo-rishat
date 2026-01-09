"""URL конфигурация для приложения items."""
from django.urls import path

from .views import (
    buy_item,
    item_page,
    success_page,
    cancel_page,
    index_page,
    create_payment_intent,
    item_payment_intent_page
)

app_name = 'items'

urlpatterns = [
    path("", index_page, name="index"),
    path("buy/<int:id>/", buy_item, name="buy_item"),
    path("item/<int:id>/", item_page, name="item_page"),
    path(
        "item/<int:id>/pay/",
        item_payment_intent_page,
        name="item_payment_intent_page"
    ),
    path("success/", success_page, name="success"),
    path("cancel/", cancel_page, name="cancel"),
    path(
        "payment-intent/<int:id>/",
        create_payment_intent,
        name="payment_intent"
    ),
]
