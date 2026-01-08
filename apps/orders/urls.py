from django.urls import path, include
from .views import (
    order_page,
    buy_order
)


urlpatterns = [
    path("order/<int:id>/", order_page),
    path("buy-order/<int:id>/", buy_order),
]