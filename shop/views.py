
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product
from importlib import import_module
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
stripe = import_module("stripe")
stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    products = Product.objects.all()

    return render(request, "shop/home.html", {
        "products": products
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "shop/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


def cart(request):
    cart_items = request.session.get("cart", {})

    products = Product.objects.filter(id__in=cart_items.keys())

    items = []
    total = 0

    for product in products:
        quantity = cart_items.get(str(product.id), 0)
        subtotal = product.price * quantity

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

        total += subtotal

    return render(
        request,
        "shop/cart.html",
        {
            "items": items,
            "total": total,
        }
    )


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True

    return redirect("cart")    


def checkout(request):
    cart_items = request.session.get("cart", {})

    products = Product.objects.filter(id__in=cart_items.keys())

    total = 0

    for product in products:
        quantity = cart_items.get(str(product.id), 0)
        total += product.price * quantity

    if total <= 0:
        return redirect("cart")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": product.name,
                    },
                    "unit_amount": int(product.price * 100),
                },
                "quantity": cart_items.get(str(product.id), 0),
            }
            for product in products
        ],
        mode="payment",
        success_url=request.build_absolute_uri("/payment-success/"),
        cancel_url=request.build_absolute_uri("/cart/"),
    )

    return redirect(session.url)

def payment_success(request):
    return render(request, "payment_success.html")