from typing import TYPE_CHECKING

from django.http import HttpRequest

from .models import Order

if TYPE_CHECKING:
    pass


def get_or_create_cart(request: HttpRequest) -> Order:
    """
    Получает или создает корзину для текущей сессии пользователя.

    Корзина хранится в сессии пользователя. Если корзина уже существует
    и не оплачена, возвращается существующая. Иначе создается новая.

    Args:
        request: HTTP запрос с сессией

    Returns:
        Объект Order (корзина) для текущей сессии
    """
    order_id = request.session.get("cart_id")

    if order_id:
        try:
            return Order.objects.get(id=order_id, is_paid=False)
        except Order.DoesNotExist:
            pass

    order = Order.objects.create()
    request.session["cart_id"] = order.id
    return order
