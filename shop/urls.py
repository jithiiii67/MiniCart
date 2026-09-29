from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),


     path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment-success/", views.payment_success, name="payment_success"),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/clear/",
        views.clear_cart,
        name="clear_cart"
    ),
]
