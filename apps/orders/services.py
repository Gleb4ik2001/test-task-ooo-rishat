from .models import Order

def get_or_create_cart(request):
    order_id = request.session.get("cart_id")

    if order_id:
        try:
            return Order.objects.get(id=order_id, is_paid=False)
        except Order.DoesNotExist:
            pass

    order = Order.objects.create()
    request.session["cart_id"] = order.id
    return order
