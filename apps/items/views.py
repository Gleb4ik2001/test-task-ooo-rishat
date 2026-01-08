import stripe

from django.conf import settings
from django.http import (
    JsonResponse,
    Http404,
    HttpRequest,
    HttpResponse
)
from django.shortcuts import get_object_or_404, render

from .models import Item


stripe.api_key = settings.STRIPE_SECRET_KEY



def index_page(request):
    items = Item.objects.all()
    return render(request, "index.html", {
        "items": items
    })


def buy_item(request: HttpRequest, id) -> JsonResponse:
    item = get_object_or_404(Item, id=id)

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.name,
                },
                "unit_amount": item.price,
            },
            "quantity": 1,
        }],
        success_url="http://localhost:8000/success/",
        cancel_url="http://localhost:8000/cancel/",
    )

    return JsonResponse({"id": session.id})


def item_page(request:HttpRequest, id) -> HttpResponse:
    item = get_object_or_404(Item, id=id)
    return render(request, "item.html", {
        "item": item,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })


def success_page(request):
    return render(request, "success.html")

def cancel_page(request):
    return render(request, "cancel.html")
