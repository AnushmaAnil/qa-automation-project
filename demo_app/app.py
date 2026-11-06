"""
ShopEasy - a tiny demo e-commerce app used as the Application Under Test (AUT).
It has a web UI (login, products, cart, checkout) and a REST API.
The test framework starts it automatically, so nothing needs to be installed or hosted.

NOTE: BUG-001 (case-sensitive search) is a deliberate, documented defect so the
project can demonstrate defect reporting and xfail handling.
"""
import re
import secrets

from flask import (Flask, jsonify, redirect, render_template, request,
                   session, url_for)

app = Flask(__name__)
app.secret_key = "demo-secret-key"

PRODUCTS = [
    {"id": 1, "name": "Backpack", "price": 1999, "category": "Bags"},
    {"id": 2, "name": "Bike Light", "price": 499, "category": "Accessories"},
    {"id": 3, "name": "Cotton T-Shirt", "price": 799, "category": "Clothing"},
    {"id": 4, "name": "Fleece Jacket", "price": 2499, "category": "Clothing"},
]
USERS = {
    "standard_user": {"password": "secret123", "locked": False},
    "locked_user": {"password": "secret123", "locked": True},
}
TOKENS = {}          # api token -> username
ORDERS = {}          # order id  -> order dict
_order_counter = {"n": 1000}


# ----------------------------------------------------------------- helpers
def find_product(pid):
    return next((p for p in PRODUCTS if p["id"] == pid), None)


def search_products(term):
    if not term:
        return list(PRODUCTS)
    # BUG-001: comparison is case-sensitive ("backpack" works, "BACKPACK" does not)
    return [p for p in PRODUCTS if term in p["name"]]


def valid_pin(pin):
    return bool(re.fullmatch(r"\d{6}", pin or ""))


def create_order(user, lines, pin_code):
    _order_counter["n"] += 1
    oid = f"ORD-{_order_counter['n']}"
    total = sum(find_product(i)["price"] * q for i, q in lines)
    ORDERS[oid] = {"order_id": oid, "user": user, "total": total,
                   "pin_code": pin_code,
                   "items": [{"product_id": i, "quantity": q} for i, q in lines]}
    return ORDERS[oid]


def cart():
    return session.setdefault("cart", {})


def cart_count():
    return sum(cart().values())


@app.context_processor
def inject_globals():
    return {"cart_count": cart_count() if "user" in session else 0}


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapper(*a, **kw):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*a, **kw)
    return wrapper


# ------------------------------------------------------------------ web UI
@app.route("/")
def home():
    return redirect(url_for("products" if "user" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        if not u:
            error = "Username is required"
        elif not p:
            error = "Password is required"
        elif u not in USERS or USERS[u]["password"] != p:
            error = "Invalid username or password"
        elif USERS[u]["locked"]:
            error = "This user account is locked"
        else:
            session.clear()
            session["user"] = u
            return redirect(url_for("products"))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/products")
@login_required
def products():
    q = request.args.get("q", "").strip()
    return render_template("products.html", products=search_products(q), q=q)


@app.route("/cart/add/<int:pid>", methods=["POST"])
@login_required
def cart_add(pid):
    if find_product(pid):
        c = cart()
        c[str(pid)] = c.get(str(pid), 0) + 1
        session.modified = True
    return redirect(request.referrer or url_for("products"))


@app.route("/cart/remove/<int:pid>", methods=["POST"])
@login_required
def cart_remove(pid):
    cart().pop(str(pid), None)
    session.modified = True
    return redirect(url_for("cart_page"))


@app.route("/cart")
@login_required
def cart_page():
    rows = [{"product": find_product(int(i)), "qty": q,
             "subtotal": find_product(int(i))["price"] * q}
            for i, q in cart().items()]
    return render_template("cart.html", rows=rows,
                           total=sum(r["subtotal"] for r in rows))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if not cart():
        return redirect(url_for("cart_page"))
    error = None
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        addr = request.form.get("address", "").strip()
        pin = request.form.get("pin_code", "").strip()
        if not name:
            error = "Full name is required"
        elif not addr:
            error = "Address is required"
        elif not valid_pin(pin):
            error = "PIN code must be exactly 6 digits"
        else:
            lines = [(int(i), q) for i, q in cart().items()]
            order = create_order(session["user"], lines, pin)
            session["cart"] = {}
            return redirect(url_for("order_done", oid=order["order_id"]))
    return render_template("checkout.html", error=error)


@app.route("/order/<oid>")
@login_required
def order_done(oid):
    order = ORDERS.get(oid)
    if not order or order["user"] != session["user"]:
        return redirect(url_for("products"))
    return render_template("order.html", order=order)


# --------------------------------------------------------------- REST API
def api_user():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return TOKENS.get(auth[7:])
    return None


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    u, p = data.get("username"), data.get("password")
    if not u or not p:
        return jsonify(error="username and password are required"), 400
    if u not in USERS or USERS[u]["password"] != p:
        return jsonify(error="invalid credentials"), 401
    if USERS[u]["locked"]:
        return jsonify(error="account locked"), 403
    token = secrets.token_hex(16)
    TOKENS[token] = u
    return jsonify(token=token, username=u), 200


@app.get("/api/products")
def api_products():
    return jsonify(search_products(request.args.get("search", "").strip())), 200


@app.get("/api/products/<int:pid>")
def api_product(pid):
    p = find_product(pid)
    return (jsonify(p), 200) if p else (jsonify(error="product not found"), 404)


@app.post("/api/orders")
def api_create_order():
    user = api_user()
    if not user:
        return jsonify(error="unauthorized"), 401
    data = request.get_json(silent=True) or {}
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return jsonify(error="items must be a non-empty list"), 400
    if not valid_pin(str(data.get("pin_code", ""))):
        return jsonify(error="pin_code must be exactly 6 digits"), 400
    lines = []
    for it in items:
        pid, qty = it.get("product_id"), it.get("quantity")
        if not isinstance(qty, int) or isinstance(qty, bool) or not 1 <= qty <= 10:
            return jsonify(error="quantity must be an integer between 1 and 10"), 400
        if not isinstance(pid, int) or not find_product(pid):
            return jsonify(error=f"product {pid} not found"), 404
        lines.append((pid, qty))
    order = create_order(user, lines, str(data["pin_code"]))
    return jsonify(order_id=order["order_id"], total=order["total"]), 201


@app.get("/api/orders/<oid>")
def api_get_order(oid):
    user = api_user()
    if not user:
        return jsonify(error="unauthorized"), 401
    order = ORDERS.get(oid)
    if not order:
        return jsonify(error="order not found"), 404
    if order["user"] != user:
        return jsonify(error="forbidden"), 403
    return jsonify(order), 200


if __name__ == "__main__":
    print("ShopEasy running at http://127.0.0.1:5000  (user: standard_user / secret123)")
    app.run(port=5000)
