from typing import Dict, Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Item
from .stripe_utils import get_stripe_keys, get_stripe_client


def index_page(request: HttpRequest) -> HttpResponse:
    """
    Отображает главную страницу со списком всех товаров.

    Args:
        request: HTTP запрос

    Returns:
        HTTP ответ с отрендеренным шаблоном index.html
    """
    items = Item.objects.all()
    return render(request, "index.html", {
        "items": items
    })


def buy_item(request: HttpRequest, id: int) -> JsonResponse:
    """
    Создает Stripe Checkout Session для оплаты товара.

    Создает сессию оплаты в Stripe для указанного товара.
    Использует правильные Stripe ключи в зависимости от валюты товара.

    Args:
        request: HTTP запрос
        id: ID товара для оплаты

    Returns:
        JSON ответ с session.id для редиректа на Stripe Checkout

    Raises:
        404: Если товар с указанным ID не найден
    """
    item = get_object_or_404(Item, id=id)

    # Получаем правильный Stripe клиент для валюты товара
    stripe_client = get_stripe_client(item.currency)

    # Формируем динамические URL
    scheme = request.scheme
    host = request.get_host()
    success_url = f"{scheme}://{host}/success/"
    cancel_url = f"{scheme}://{host}/cancel/"

    session = stripe_client.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": item.currency,
                "product_data": {
                    "name": item.name,
                },
                "unit_amount": item.price,
            },
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return JsonResponse({"id": session.id})


def item_page(request: HttpRequest, id: int) -> HttpResponse:
    """
    Отображает страницу товара с кнопкой оплаты.

    Args:
        request: HTTP запрос
        id: ID товара

    Returns:
        HTTP ответ с отрендеренным шаблоном item.html

    Raises:
        404: Если товар с указанным ID не найден
    """
    item = get_object_or_404(Item, id=id)
    # Получаем правильный публичный ключ для валюты товара
    _, public_key = get_stripe_keys(item.currency)
    return render(request, "item.html", {
        "item": item,
        "stripe_public_key": public_key
    })


def success_page(request: HttpRequest) -> HttpResponse:
    """
    Отображает страницу успешной оплаты.

    Args:
        request: HTTP запрос

    Returns:
        HTTP ответ с отрендеренным шаблоном success.html
    """
    return render(request, "success.html")


def cancel_page(request: HttpRequest) -> HttpResponse:
    """
    Отображает страницу отмены оплаты.

    Args:
        request: HTTP запрос

    Returns:
        HTTP ответ с отрендеренным шаблоном cancel.html
    """
    return render(request, "cancel.html")


def item_payment_intent_page(
    request: HttpRequest,
    id: int
) -> HttpResponse:
    """
    Отображает страницу товара с формой оплаты через Payment Intent.

    Позволяет пользователю оплатить товар без перенаправления
    на страницу Stripe. Оплата происходит прямо на сайте.

    Args:
        request: HTTP запрос
        id: ID товара

    Returns:
        HTTP ответ с отрендеренным шаблоном item_payment_intent.html

    Raises:
        404: Если товар с указанным ID не найден
    """
    item = get_object_or_404(Item, id=id)
    # Получаем правильный публичный ключ для валюты товара
    _, public_key = get_stripe_keys(item.currency)
    return render(request, "item_payment_intent.html", {
        "item": item,
        "stripe_public_key": public_key
    })


def create_payment_intent(
    request: HttpRequest,
    id: int
) -> JsonResponse:
    """
    Создает Payment Intent для оплаты товара (бонусная задача).

    Альтернатива Checkout Session для более гибкого управления
    процессом оплаты. Payment Intent позволяет контролировать
    процесс оплаты на стороне клиента.

    Args:
        request: HTTP запрос
        id: ID товара для оплаты

    Returns:
        JSON ответ с client_secret и payment_intent_id

    Raises:
        404: Если товар с указанным ID не найден
        400: Если произошла ошибка при создании Payment Intent
    """
    item = get_object_or_404(Item, id=id)

    # Получаем правильный Stripe клиент для валюты товара
    stripe_client = get_stripe_client(item.currency)

    try:
        # Создаем Payment Intent
        intent = stripe_client.PaymentIntent.create(
            amount=item.price,
            currency=item.currency,
            metadata={
                'item_id': item.id,
                'item_name': item.name,
            },
        )

        return JsonResponse({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
