from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from .models import User
from .db import db
from .utils import hash_password, verify_password

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    """FR1.1: User registration with username, password, email"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    email = data.get("email", "").strip()

    if not all([username, password, email]):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email exists"}), 409

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role="customer"
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"user": user.to_dict()}), 201


@bp.route("/login", methods=["POST"])
def login():
    """FR1.2: User login with username + password"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "username": user.username})
    return jsonify({"access_token": token, "user": user.to_dict()}), 200
