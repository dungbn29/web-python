from flask import Blueprint, render_template, request, redirect, session, flash
import hashlib

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from db import users_col
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        user = users_col.find_one({"email": email, "password": password})
        if user:
            session["user"] = email
            session["user_name"] = user.get("name", "User")
            session["role"] = user.get("role", "user")
            if user.get("role") == "admin":
                return redirect("/admin")
            return redirect("/")
        flash("Sai thông tin đăng nhập")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    from db import users_col
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        if users_col.find_one({"email": email}):
            flash("Email đã tồn tại")
            return redirect("/register")
        users_col.insert_one({"email": email, "password": password, "name": name, "role": "user"})
        session["user"] = email
        session["user_name"] = name
        session["role"] = "user"
        flash("Đăng ký thành công")
        return redirect("/")
    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")