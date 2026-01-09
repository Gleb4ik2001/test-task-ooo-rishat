from django.urls import path

from .views import (
    decrease_item,
    order_page,
    buy_order,
    add_to_cart,
    cart_page,
    remove_from_cart,
    apply_discount,
    remove_discount
)

app_name = 'orders'

urlpatterns = [
    path("order/<int:id>/", order_page, name="order_page"),
    path("buy-order/<int:id>/", buy_order, name="buy_order"),
    path("add-to-cart/<int:item_id>/", add_to_cart, name="add_to_cart"),
    path("remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("decrease/<int:item_id>/", decrease_item, name="decrease_item"),
    path("cart/", cart_page, name="cart"),
    path("apply-discount/", apply_discount, name="apply_discount"),
    path("remove-discount/", remove_discount, name="remove_discount"),
]
