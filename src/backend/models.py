from datetime import datetime
from .db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="customer")  # customer or manager

    orders = db.relationship("Order", backref="user")

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email, "role": self.role}


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    price_buy = db.Column(db.Float, nullable=False)
    price_rent = db.Column(db.Float, nullable=False)
    available = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "price_buy": self.price_buy,
            "price_rent": self.price_rent,
            "available": self.available,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    kind = db.Column(db.String(10), nullable=False)  # buy or rent
    status = db.Column(db.String(20), default="Pending")  # Pending, Paid, etc
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order")

    def to_dict(self, include_items=False):
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "kind": self.kind,
            "status": self.status,
            "total": self.total,
            "created_at": self.created_at.isoformat(),
        }
        if include_items:
            result["items"] = [item.to_dict() for item in self.items]
        return result


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float)

    book = db.relationship("Book")

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "title": self.book.title,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
        }
