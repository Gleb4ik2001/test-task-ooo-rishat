from django.urls import path, include
from .views import (
    decrease_item,
    order_page,
    buy_order,
    add_to_cart,
    cart_page,
    remove_from_cart
)


urlpatterns = [
    path("order/<int:id>/", order_page),
    path("buy-order/<int:id>/", buy_order),
    path("add-to-cart/<int:item_id>/", add_to_cart),
    path("remove/<int:item_id>/", remove_from_cart),
    path("decrease/<int:item_id>/", decrease_item),
    path("cart/", cart_page),
]