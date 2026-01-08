from django.urls import path
from .views import (
    buy_item,
    item_page,
    success_page,
    cancel_page,
    index_page
)


urlpatterns = [
    path("", index_page, name="index"),
    path("buy/<int:id>/", buy_item),
    path("item/<int:id>/", item_page),
    path("success/", success_page),
    path("cancel/", cancel_page)
]