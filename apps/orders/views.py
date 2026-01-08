import stripe

from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages

from .services import get_or_create_cart
from .models import Order, OrderItem, Discount
from items.models import Item


stripe.api_key = settings.STRIPE_SECRET_KEY


def order_page(request:HttpRequest, id)-> HttpResponse:
    order : get_object_or_404 = get_object_or_404(Order, id=id)
    return render(request, "order.html", {
        "order": order,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })


def buy_order(request:HttpRequest, id):
    order = get_object_or_404(Order, id=id)

    line_items = []
    total_multiplier = 1

    if order.discount:
        total_multiplier -= order.discount.percent / 100

    if order.tax:
        total_multiplier += order.tax.percent / 100

    for oi in order.items.all():
        price = int(oi.item.price * total_multiplier)

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": oi.item.name,
                },
                "unit_amount": price,
            },
            "quantity": oi.quantity,
        })
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url="http://127.0.0.1:8000/success/",
        cancel_url="http://127.0.0.1:8000/orders/cart/",
    )

    return redirect(session.url)


def add_to_cart(request:HttpRequest, item_id) -> HttpResponseRedirect:
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


def remove_from_cart(request:HttpRequest, item_id):
    cart = get_or_create_cart(request)
    oi = get_object_or_404(OrderItem, order=cart, item_id=item_id)
    oi.delete()
    return redirect("/orders/cart/")


def decrease_item(request:HttpRequest, item_id) -> HttpResponseRedirect:
    cart = get_or_create_cart(request)
    oi = get_object_or_404(OrderItem, order=cart, item_id=item_id)

    if oi.quantity > 1:
        oi.quantity -= 1
        oi.save()
    else:
        oi.delete()

    return redirect("/orders/cart/")


def cart_page(request:HttpRequest)-> HttpResponse:
    cart = get_or_create_cart(request)
    return render(request, "cart.html", {"order": cart})