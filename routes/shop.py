from flask import Blueprint, render_template, request, redirect, session, jsonify, flash
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
    from db import phones_col
    cart = session.get("cart", {})
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    cart_items = []
    for item in cart.values():
        phone = phones_col.find_one({"name": item["name"]})
        cart_items.append({
            "name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"],
            "image": phone["image"] if phone else "no-image.jpg"
        })
    return render_template("cart.html", cart=cart_items, total=total)

@shop_bp.route("/remove_from_cart/<string:name>")
def remove_from_cart(name):
    cart = session.get("cart", {})
    if name in cart:
        del cart[name]
        session["cart"] = cart
    return redirect("/cart")

@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout_page():
    from db import phones_col, orders_col
    if request.method == "POST":
        if "user" not in session:
            return redirect("/login")
        cart = session.get("cart", {})
        if not cart:
            return redirect("/cart")
        fullname = request.form.get("fullname")
        address = request.form.get("address")
        phone_number = request.form.get("phone")
        payment_method = request.form.get("payment_method")
        
        orders_col.insert_one({
            "user": session["user"],
            "fullname": fullname,
            "address": address,
            "phone": phone_number,
            "payment_method": payment_method,
            "items": list(cart.values()),
            "total": sum(i["price"] * i["quantity"] for i in cart.values()),
            "date": datetime.utcnow(),
            "status": "pending"
        })
        for name, item in cart.items():
            phones_col.update_one({"name": name}, {"$inc": {"stock": -item["quantity"]}})
        session.pop("cart", None)
        flash("Đặt hàng thành công!", "success")
        return redirect("/")
    # GET request
    if "user" not in session:
        return redirect("/login")
    cart = session.get("cart", {})
    if not cart:
        return redirect("/cart")
    return render_template("checkout.html", success=False)

@shop_bp.route('/update_cart', methods=['POST'])
def update_cart():
    from db import phones_col
    
    data = request.get_json()
    name = data['name']
    action = data['action']
    
    cart = session.get('cart', {})
    if name not in cart:
        return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại trong giỏ hàng'})
    
    # Cập nhật số lượng
    if action == 'increase':
        cart[name]['quantity'] += 1
    elif action == 'decrease':
        if cart[name]['quantity'] <= 1:
            return jsonify({'success': False, 'message': 'Số lượng tối thiểu là 1'})
        cart[name]['quantity'] -= 1
    
    # Kiểm tra tồn kho
    phone = phones_col.find_one({'name': name})
    if phone and phone.get('stock', 0) < cart[name]['quantity']:
        return jsonify({'success': False, 'message': 'Số lượng vượt quá tồn kho'})
    
    session['cart'] = cart
    
    # Tính toán giá mới
    new_price = cart[name]['price'] * cart[name]['quantity']
    new_total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    return jsonify({
        'success': True,
        'newQuantity': cart[name]['quantity'],
        'newPrice': new_price,
        'newTotal': new_total
    })

