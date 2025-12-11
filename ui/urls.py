from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("toggle/", views.toggle_bot, name="toggle"),
    path("buy/", views.buy, name="buy"),
    path("sell/", views.sell, name="sell"),
    path("price/", views.price_json, name="price_json"),
]
