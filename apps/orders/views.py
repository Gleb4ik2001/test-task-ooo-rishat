from typing import Dict, Any

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .services import get_or_create_cart
from .models import Order, OrderItem, Discount
from items.models import Item
from .stripe_utils import get_stripe_keys, get_stripe_client


def order_page(request: HttpRequest, id: int) -> HttpResponse:
    """
    Отображает страницу заказа с кнопкой оплаты.

    Args:
        request: HTTP запрос
        id: ID заказа

    Returns:
        HTTP ответ с отрендеренным шаблоном order.html

    Raises:
        404: Если заказ с указанным ID не найден
    """
    order = get_object_or_404(Order, id=id)

    # Определяем валюту заказа (берем из первого товара)
    # Предполагаем, что все товары в заказе в одной валюте
    currency = 'usd'  # по умолчанию
    if order.items.exists():
        currency = order.items.first().item.currency

    # Получаем правильный публичный ключ для валюты
    _, public_key = get_stripe_keys(currency)

    return render(request, "order.html", {
        "order": order,
        "stripe_public_key": public_key
    })


def buy_order(request: HttpRequest, id: int) -> JsonResponse:
    """
    Создает Stripe Checkout Session для оплаты заказа.

    Создает сессию оплаты в Stripe для указанного заказа.
    Применяет скидку и налог к товарам в заказе.
    Использует правильные Stripe ключи в зависимости от валюты.

    Args:
        request: HTTP запрос
        id: ID заказа для оплаты

    Returns:
        JSON ответ с session.id для редиректа на Stripe Checkout

    Raises:
        404: Если заказ с указанным ID не найден
        400: Если заказ пуст
    """
    order = get_object_or_404(Order, id=id)

    if not order.items.exists():
        return JsonResponse({"error": "Order is empty"}, status=400)

    # Определяем валюту заказа (берем из первого товара)
    # Предполагаем, что все товары в заказе в одной валюте
    currency = order.items.first().item.currency

    # Получаем правильный Stripe клиент для валюты
    stripe_client = get_stripe_client(currency)

    # Формируем line_items с оригинальными ценами
    # Скидка и налог будут применены через Stripe API
    line_items = []
    for oi in order.items.all():
        line_items.append({
            "price_data": {
                "currency": oi.item.currency,
                "product_data": {
                    "name": oi.item.name,
                },
                "unit_amount": oi.item.price,
            },
            "quantity": oi.quantity,
        })

    # Формируем динамические URL
    scheme = request.scheme
    host = request.get_host()
    success_url = f"{scheme}://{host}/success/"
    cancel_url = f"{scheme}://{host}/orders/cart/"

    # Настройка параметров для Stripe Session
    session_params: Dict[str, Any] = {
        "mode": "payment",
        "line_items": line_items,
        "success_url": success_url,
        "cancel_url": cancel_url,
    }

    # Добавляем скидку через discounts, если она есть
    # Для правильного отображения в Stripe Checkout используем discounts
    # Для упрощения, применяем скидку через расчет line_items
    if order.discount:
        # Пересчитываем line_items с учетом скидки
        subtotal = sum(
            oi.item.price * oi.quantity for oi in order.items.all()
        )
        discounted_total = subtotal * (100 - order.discount.percent) // 100

        # Распределяем скидку пропорционально между товарами
        if subtotal > 0:
            discount_multiplier = discounted_total / subtotal
            line_items = []
            for oi in order.items.all():
                discounted_price = int(oi.item.price * discount_multiplier)
                line_items.append({
                    "price_data": {
                        "currency": oi.item.currency,
                        "product_data": {
                            "name": oi.item.name,
                        },
                        "unit_amount": discounted_price,
                    },
                    "quantity": oi.quantity,
                })
            session_params["line_items"] = line_items

    # Добавляем налог через automatic_tax, если он есть
    # Для правильного отображения в Stripe Checkout используем automatic_tax
    # Для упрощения, применяем налог через расчет line_items
    if order.tax:
        # Пересчитываем line_items с учетом налога
        current_total = sum(
            item["price_data"]["unit_amount"] * item["quantity"]
            for item in session_params["line_items"]
        )
        taxed_total = current_total * (100 + order.tax.percent) // 100

        # Распределяем налог пропорционально между товарами
        if current_total > 0:
            tax_multiplier = taxed_total / current_total
            line_items = []
            for item in session_params["line_items"]:
                original_price = item["price_data"]["unit_amount"]
                taxed_price = int(original_price * tax_multiplier)
                line_items.append({
                    "price_data": {
                        "currency": item["price_data"]["currency"],
                        "product_data": {
                            "name": item["price_data"]["product_data"]["name"],
                        },
                        "unit_amount": taxed_price,
                    },
                    "quantity": item["quantity"],
                })
            session_params["line_items"] = line_items

    session = stripe_client.checkout.Session.create(**session_params)

    return JsonResponse({"id": session.id})


def add_to_cart(
    request: HttpRequest,
    item_id: int
) -> HttpResponseRedirect:
    """
    Добавляет товар в корзину.

    Если товар уже есть в корзине, увеличивает его количество на 1.
    Иначе создает новую запись в корзине.

    Args:
        request: HTTP запрос
        item_id: ID товара для добавления

    Returns:
        Редирект на предыдущую страницу или главную
    """
    cart = get_or_create_cart(request)
    item = Item.objects.get(id=item_id)

    order_item, created = OrderItem.objects.get_or_create(
        order=cart,
        item=item
    )

    if not created:
        order_item.quantity += 1
        order_item.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))


def remove_from_cart(
    request: HttpRequest,
    item_id: int
) -> HttpResponseRedirect:
    """
    Удаляет товар из корзины.

    Args:
        request: HTTP запрос
        item_id: ID товара для удаления

    Returns:
        Редирект на страницу корзины

    Raises:
        404: Если товар не найден в корзине
    """
    cart = get_or_create_cart(request)
    order_item = get_object_or_404(
        OrderItem,
        order=cart,
        item_id=item_id
    )
    order_item.delete()
    return redirect("/orders/cart/")


def decrease_item(
    request: HttpRequest,
    item_id: int
) -> HttpResponseRedirect:
    """
    Уменьшает количество товара в корзине на 1.

    Если количество становится 0, товар удаляется из корзины.

    Args:
        request: HTTP запрос
        item_id: ID товара

    Returns:
        Редирект на страницу корзины

    Raises:
        404: Если товар не найден в корзине
    """
    cart = get_or_create_cart(request)
    order_item = get_object_or_404(
        OrderItem,
        order=cart,
        item_id=item_id
    )

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()

    return redirect("/orders/cart/")


def cart_page(request: HttpRequest) -> HttpResponse:
    """
    Отображает страницу корзины с товарами и формой для скидки.

    Вычисляет промежуточную сумму, сумму скидки, налог и итоговую сумму.
    Передает все необходимые данные для отображения и оплаты.

    Args:
        request: HTTP запрос

    Returns:
        HTTP ответ с отрендеренным шаблоном cart.html
    """
    cart = get_or_create_cart(request)

    # Определяем валюту заказа (берем из первого товара)
    currency = 'usd'  # по умолчанию
    if cart.items.exists():
        currency = cart.items.first().item.currency

    # Получаем правильный публичный ключ для валюты
    _, public_key = get_stripe_keys(currency)

    # Вычисляем суммы для отображения
    subtotal = cart.subtotal() / 100 if cart.items.exists() else 0
    discount_amount = 0
    if cart.discount and cart.items.exists():
        discount_amount = subtotal * cart.discount.percent / 100
    tax_amount = 0
    if cart.tax and cart.items.exists():
        # Налог применяется к сумме после скидки
        amount_after_discount = subtotal - discount_amount
        tax_amount = amount_after_discount * cart.tax.percent / 100
    total = (cart.total_amount() / 100) if cart.items.exists() else 0

    return render(request, "cart.html", {
        "order": cart,
        "stripe_public_key": public_key,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "total": total,
        "currency": currency.upper()
    })


def apply_discount(request: HttpRequest) -> HttpResponseRedirect:
    """
    Применяет скидку к корзине по коду.

    Ищет скидку по коду и применяет ее к текущей корзине.
    Показывает сообщение об успехе или ошибке.

    Args:
        request: HTTP запрос с POST данными, содержащими discount_code

    Returns:
        Редирект на страницу корзины с сообщением о результате
    """
    if request.method == 'POST':
        discount_code = request.POST.get('discount_code', '').strip()

        if not discount_code:
            messages.error(request, 'Пожалуйста, введите код скидки')
            return redirect('/orders/cart/')

        try:
            discount = Discount.objects.get(code=discount_code)
            cart = get_or_create_cart(request)
            cart.discount = discount
            cart.save()
            messages.success(
                request,
                f'Скидка "{discount.name}" применена!'
            )
        except Discount.DoesNotExist:
            messages.error(request, 'Код скидки не найден')

        return redirect('/orders/cart/')

    return redirect('/orders/cart/')


def remove_discount(request: HttpRequest) -> HttpResponseRedirect:
    """
    Удаляет примененную скидку из корзины.

    Args:
        request: HTTP запрос

    Returns:
        Редирект на страницу корзины с сообщением об удалении
    """
    cart = get_or_create_cart(request)
    if cart.discount:
        discount_name = cart.discount.name
        cart.discount = None
        cart.save()
        messages.info(request, f'Скидка "{discount_name}" удалена')
    return redirect('/orders/cart/')
