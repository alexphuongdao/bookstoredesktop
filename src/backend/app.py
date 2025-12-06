
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .db import db
from .config import DATABASE_URL, JWT_SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
from .models import User, Book, Order, OrderItem
from .utils import hash_password, generate_bill, save_bill, send_bill_email


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

    db.init_app(app)
    jwt = JWTManager(app)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # ==================== BOOKS ====================

    @app.get("/books")
    def list_books():
        """FR2.1-2.3: Search books by keyword (title/author), display with prices"""
        query = request.args.get("q", "").strip()
        
        if query:
            books = Book.query.filter(
                (Book.title.ilike(f"%{query}%")) |
                (Book.author.ilike(f"%{query}%"))
            ).all()
        else:
            books = Book.query.all()
        
        return jsonify([b.to_dict() for b in books]), 200

    @app.post("/books")
    @jwt_required()
    def create_book():
        """FR5.4: Manager can create books"""
        from flask_jwt_extended import get_jwt
        
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")
        
        if role != "manager":
            return jsonify({"error": "Manager only"}), 403

        data = request.get_json() or {}
        title = data.get("title", "").strip()
        author = data.get("author", "").strip()
        
        try:
            price_buy = float(data.get("price_buy", 0.0))
            price_rent = float(data.get("price_rent", 0.0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid prices"}), 400

        if not title or not author:
            return jsonify({"error": "Missing fields"}), 400

        book = Book(title=title, author=author, price_buy=price_buy, price_rent=price_rent)
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    

    @app.put("/books/<int:book_id>")
    @jwt_required()
    def update_book(book_id):
        """FR5.4: Manager can update books"""
        from flask_jwt_extended import get_jwt
        
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")
        
        if role != "manager":
            return jsonify({"error": "Manager only"}), 403

        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json() or {}
        if "title" in data:
            book.title = data["title"]
        if "author" in data:
            book.author = data["author"]
        if "price_buy" in data:
            book.price_buy = data["price_buy"]
        if "price_rent" in data:
            book.price_rent = data["price_rent"]
        if "available" in data:
            book.available = data["available"]

        db.session.commit()
        return jsonify(book.to_dict()), 200

    @app.patch("/books/<int:book_id>/add-quantity")
    @jwt_required()
    def add_book_quantity(book_id):
        """FR5.4: Manager adds quantity to existing available (for rent returns)"""
        from flask_jwt_extended import get_jwt
        
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")
        
        if role != "manager":
            return jsonify({"error": "Manager only"}), 403

        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json() or {}
        quantity = data.get("quantity", 0)
        
        if not isinstance(quantity, int) or quantity < 0:
            return jsonify({"error": "Quantity must be a non-negative integer"}), 400

        # ADD to existing available (because this is rent returns, not adjust quantity)
        book.available += quantity
        db.session.commit()
        return jsonify(book.to_dict()), 200

    # ==================== ORDERS ====================

    @app.post("/orders")
    @jwt_required()
    def create_order():
        """FR3.1-3.3: Place buy or rent order with multiple items"""
        from flask_jwt_extended import get_jwt
        
        identity = get_jwt_identity()
        user_id = int(identity)

        data = request.get_json() or {}
        kind = data.get("kind", "buy").lower()
        items_data = data.get("items", [])

        if kind not in ["buy", "rent"]:
            return jsonify({"error": "Invalid kind"}), 400

        if not items_data:
            return jsonify({"error": "No items"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        order = Order(user_id=user_id, kind=kind)
        total = 0.0

        for item_data in items_data:
            book_id = item_data.get("book_id")
            quantity = int(item_data.get("quantity", 1))

            book = Book.query.get(book_id)
            if not book:
                return jsonify({"error": f"Book {book_id} not found"}), 404

            unit_price = book.price_buy if kind == "buy" else book.price_rent
            total += unit_price * quantity

            order_item = OrderItem(book_id=book_id, quantity=quantity, unit_price=unit_price)
            order.items.append(order_item)

        order.total = total
        db.session.add(order)
        db.session.commit()

        
        bill = generate_bill(order, user)
        bill_path = save_bill(bill)

        
        email_sent = send_bill_email(bill, user.email, None)

        return jsonify({
            "order": order.to_dict(include_items=True),
            "bill": bill,
            "email_sent": email_sent,
        }), 201

    @app.get("/orders")
    @jwt_required()
    def list_orders():
        """FR5.2: Manager sees all orders, customers see their own"""
        from flask_jwt_extended import get_jwt
        
        identity = get_jwt_identity()
        user_id = int(identity)
        claims = get_jwt()
        role = claims.get("role")

        if role == "manager":
            orders = Order.query.all()
        else:
            orders = Order.query.filter_by(user_id=user_id).all()

        return jsonify([o.to_dict(include_items=True) for o in orders]), 200

    @app.patch("/orders/<int:order_id>/status")
    @jwt_required()
    def update_order_status(order_id):
        """FR5.3: Manager updates payment status"""
        from flask_jwt_extended import get_jwt
        
        claims = get_jwt()
        role = claims.get("role")
        if role != "manager":
            return jsonify({"error": "Manager only"}), 403

        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json() or {}
        status = data.get("status", "").strip()

        if not status:
            return jsonify({"error": "Missing status"}), 400

        order.status = status
        db.session.commit()
        return jsonify({"order": order.to_dict(include_items=True)}), 200

    # ==================== INIT ====================

    with app.app_context():
        db.create_all()

        # Create manager user
        if not User.query.filter_by(username=ADMIN_USERNAME).first():
            manager = User(
                username=ADMIN_USERNAME,
                email=f"{ADMIN_USERNAME}@local",
                password_hash=hash_password(ADMIN_PASSWORD),
                role="manager"
            )
            db.session.add(manager)
            db.session.commit()
            print(f"✓ Manager user created: {ADMIN_USERNAME}")

        # sample books for testing basic first, add more later
        if Book.query.count() == 0:
            sample_books = [
                ("The Pragmatic Programmer", "David Thomas & Andrew Hunt", 49.99, 9.99),
                ("Clean Code", "Robert C. Martin", 39.99, 7.99),
                ("Design Patterns", "Gang of Four", 54.99, 10.99),
            ]
            for title, author, buy_price, rent_price in sample_books:
                db.session.add(Book(title=title, author=author, price_buy=buy_price, price_rent=rent_price))
            db.session.commit()
            print(f"✓ Seeded {len(sample_books)} books")

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n🚀 Bookstore API running on http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001, debug=True)
