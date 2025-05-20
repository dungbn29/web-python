from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime

shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/")
def index():
    from db import phones_col
    phones = list(phones_col.find())
    return render_template("index.html", phones=phones)

@shop_bp.route("/product/<string:name>")
def product_detail(name):
    from db import phones_col
    phone = phones_col.find_one({"name": name})
    return render_template("product.html", phone=phone)

@shop_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    from db import phones_col
    name = request.form["name"]
    quantity = int(request.form.get("quantity", 1))
    phone = phones_col.find_one({"name": name})
    if not phone:
        return redirect("/")
    cart = session.get("cart", {})
    if name in cart:
        cart[name]["quantity"] += quantity
    else:
        cart[name] = {
            "name": name,
            "price": phone["price"],
            "quantity": quantity
        }
    session["cart"] = cart
    return redirect("/cart")

@shop_bp.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    return render_template("cart.html", cart=cart.values(), total=total)

@shop_bp.route("/remove_from_cart/<string:name>")
def remove_from_cart(name):
    cart = session.get("cart", {})
    if name in cart:
        del cart[name]
        session["cart"] = cart
    return redirect("/cart")

@shop_bp.route("/checkout", methods=["POST"])
def checkout():
    from db import phones_col
    if "user" not in session:
        return redirect("/login")
    cart = session.get("cart", {})
    if not cart:
        return redirect("/cart")
    db = phones_col.database
    db.orders.insert_one({
        "user": session["user"],
        "items": list(cart.values()),
        "total": sum(i["price"] * i["quantity"] for i in cart.values()),
        "date": datetime.utcnow()
    })
    for name, item in cart.items():
        phones_col.update_one({"name": name}, {"$inc": {"stock": -item["quantity"]}})
    session.pop("cart")
    return "Đặt hàng thành công!"