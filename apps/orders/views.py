import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Order


stripe.api_key = settings.STRIPE_SECRET_KEY


def order_page(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, "order.html", {
        "order": order,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })


def buy_order(request, id):
    order = get_object_or_404(Order, id=id)

    line_items = []
    for oi in order.items.all():
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": oi.item.name,
                },
                "unit_amount": oi.item.price,
            },
            "quantity": oi.quantity,
        })

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url="http://127.0.0.1:8000/success/",
        cancel_url="http://127.0.0.1:8000/cancel/",
    )

    return JsonResponse({"id": session.id})
