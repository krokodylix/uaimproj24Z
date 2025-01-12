# app.py

import os

from flask_cors import CORS
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode, b64decode
from datetime import datetime
from sqlalchemy import func  # Dodany import

from db_models import db, User, Product, TransportType, Order, Province

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    # Konfiguracja bazy danych
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'change_me_in_env')

    # Nadpisanie konfiguracji w trybie testów (jeśli przekazano)
    if test_config:
        for key, value in test_config.items():
            app.config[key] = value

    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

        # --- Tworzenie konta admina (jeśli nie istnieje) ---
        ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'secret')

        admin_user = User.query.filter_by(username=ADMIN_USERNAME).first()
        if not admin_user:
            hashed_admin_password = generate_password_hash(ADMIN_PASSWORD)
            new_admin = User(
                username=ADMIN_USERNAME,
                email="admin@example.com",
                password=hashed_admin_password,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()

    @app.route('/')
    def home():
        return "Witaj w sklepie rolniczym backend!"

    # --------------------- REJESTRACJA ---------------------
    @app.route('/register', methods=['POST'])
    def register():
        """
        Endpoint rejestracji zwykłego użytkownika.
        Jeżeli próbuje zarejestrować się ktoś o nazwie ADMIN_USERNAME (z .env),
        to blokujemy (admin jest już utworzony).

        Input JSON:
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
        """
        ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')

        data = request.get_json()
        if not data:
            return jsonify({"msg": "Brak danych w żądaniu"}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"msg": "Nieprawidłowe dane"}), 400

        # Sprawdzamy, czy to nie próba rejestracji admina
        if username == ADMIN_USERNAME:
            return jsonify({"msg": "Nie można zarejestrować konta admina"}), 403

        # Sprawdzamy, czy użytkownik już istnieje
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            return jsonify({"msg": "Użytkownik o takiej nazwie lub emailu już istnieje"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "Rejestracja zakończona sukcesem"}), 201

    # --------------------- LOGOWANIE (dla wszystkich) ---------------------
    @app.route('/login', methods=['POST'])
    def login():
        """
        Wspólny endpoint logowania (także dla admina).
        Podajemy email, password -> sprawdzamy w bazie.
        Jeśli OK, zwracamy token z identity = user.id.

        Input JSON:
        {
            "email": "string",
            "password": "string"
        }
        """
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Brak danych w żądaniu"}), 400

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"msg": "Nieprawidłowe dane"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"msg": "Błędny email lub hasło"}), 401

        # Tworzymy access_token z user.id
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    # --------------------- DANE UŻYTKOWNIKA ---------------------
    @app.route('/user', methods=['GET'])
    @jwt_required()
    def get_user():
        """
        Retrieves user details for the currently logged-in user.
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }), 200

    # --------------------- PRODUKTY ---------------------
    @app.route('/product', methods=['POST'])
    @jwt_required()
    def add_product():
        """
        Dodawanie nowego produktu - wyłącznie przez admina.
        Body JSON: { "description": "...", "price": 10.99, "image": "base64?" }

        Input JSON:
        {
            "description": "string",
            "price": float,
            "image": "base64 string (optional)"
        }
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"msg": "Brak uprawnień"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"msg": "Brak danych w żądaniu"}), 400

        description = data.get('description')
        price = data.get('price')
        image_base64 = data.get('image')

        if description is None or price is None:
            return jsonify({"msg": "Opis i cena są wymagane"}), 400

        image_bytes = None
        if image_base64:
            try:
                image_bytes = b64decode(image_base64)
            except Exception:
                return jsonify({"msg": "Niepoprawny format obrazu"}), 400

        new_product = Product(description=description, price=price, image=image_bytes)
        db.session.add(new_product)
        db.session.commit()

        return jsonify({"msg": "Produkt dodany", "product_id": new_product.id}), 201

    @app.route('/products', methods=['GET'])
    def get_all_products():
        """
        Zwraca listę wszystkich produktów w formie JSON.
        Pole image (o ile istnieje w bazie) jest zwracane w formacie base64.

        Input: None
        """
        products = Product.query.all()
        result = []
        for product in products:
            image_base64 = b64encode(product.image).decode('utf-8') if product.image else None
            result.append({
                "id": product.id,
                "description": product.description,
                "price": product.price,
                "image": image_base64
            })
        return jsonify(result), 200

    @app.route('/product/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        """
        Pobiera produkt o danym ID i zwraca go w formacie JSON.
        W polu image zwracamy base64-encoded, jeśli istnieje.

        Input:
            - URL Parameter: product_id (integer)
        """
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Produkt nie istnieje"}), 404

        image_base64 = b64encode(product.image).decode('utf-8') if product.image else None
        return jsonify({
            "id": product.id,
            "description": product.description,
            "price": product.price,
            "image": image_base64
        }), 200

    # --------------------- EDYCJA PRODUKTU ---------------------
    @app.route('/product/<int:product_id>', methods=['PUT'])
    @jwt_required()
    def edit_product(product_id):
        """
        Edytuje istniejący produkt - wyłącznie przez admina.
        Body JSON może zawierać dowolne z pól: "description", "price", "image".

        Input JSON:
        {
            "description": "string (optional)",
            "price": float (optional),
            "image": "base64 string or empty string to remove (optional)"
        }
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"msg": "Brak uprawnień"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"msg": "Brak danych w żądaniu"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Produkt nie istnieje"}), 404

        description = data.get('description')
        price = data.get('price')
        image_base64 = data.get('image')

        # Aktualizacja pól, jeśli są dostarczone
        if description is not None:
            product.description = description
        if price is not None:
            if not isinstance(price, (int, float)):
                return jsonify({"msg": "Cena musi być liczbą"}), 400
            product.price = price
        if image_base64 is not None:
            if image_base64 == "":
                product.image = None  # Możliwość usunięcia obrazu
            else:
                try:
                    product.image = b64decode(image_base64)
                except Exception:
                    return jsonify({"msg": "Niepoprawny format obrazu"}), 400

        db.session.commit()

        return jsonify({"msg": "Produkt zaktualizowany"}), 200

    # --------------------- ZAMÓWIENIA ---------------------
    @app.route('/order', methods=['POST'])
    @jwt_required()
    def create_order():
        """
        Tworzy zamówienie dla zalogowanego użytkownika.
        JSON body:
        {
          "product_id": 123,
          "delivery_date": "2025-05-20",
          "address": "ul. Rolna 10, 00-000 Warszawa",
          "transport_type": "TRUCK",    # lub "COURIER", "COURIER"
          "province": "mazowieckie"     # Nowe pole
        }

        Input JSON:
        {
            "product_id": integer,
            "delivery_date": "YYYY-MM-DD",
            "address": "string",
            "transport_type": "string",  # "TRUCK", "COURIER", or "COURIER"
            "province": "string"         # e.g., "mazowieckie"
        }
        """
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Brak danych w żądaniu"}), 400

        current_user_id = get_jwt_identity()
        product_id = data.get('product_id')
        delivery_date = data.get('delivery_date')
        address = data.get('address')
        transport_type_str = data.get('transport_type')
        province_str = data.get('province')  # Nowe pole

        if not product_id or not delivery_date or not address or not transport_type_str or not province_str:
            return jsonify({"msg": "Niekompletne dane zamówienia"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Produkt nie istnieje"}), 404

        valid_transports = [t.value for t in TransportType]
        if transport_type_str not in valid_transports:
            return jsonify({
                "msg": f"Nieprawidłowy środek transportu. Dozwolone: {valid_transports}"
            }), 400

        valid_provinces = [p.value for p in Province]
        if province_str not in valid_provinces:
            return jsonify({
                "msg": f"Nieprawidłowe województwo. Dozwolone: {valid_provinces}"
            }), 400

        # Pobranie wartości enum dla województwa
        province_enum = Province(province_str)

        new_order = Order(
            user_id=current_user_id,
            product_id=product_id,
            delivery_date=delivery_date,
            address=address,
            transport_type=transport_type_str,
            province=province_enum
        )
        db.session.add(new_order)
        db.session.commit()

        return jsonify({"msg": "Zamówienie utworzone pomyślnie", "order_id": new_order.id}), 201

    @app.route('/order/<int:order_id>', methods=['GET'])
    @jwt_required()
    def get_order(order_id):
        """
        Zwraca szczegóły zamówienia o podanym ID, ale tylko jeśli
        zalogowany użytkownik (JWT) jest autorem zamówienia.

        Input:
            - URL Parameter: order_id (integer)
        """
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        if not order or order.user_id != current_user_id:
            return jsonify({"msg": "Brak dostępu do tego zamówienia"}), 403

        product = Product.query.get(order.product_id)
        image_base64 = b64encode(product.image).decode('utf-8') if product.image else None
        return jsonify({
            "order_id": order.id,
            "user_id": order.user_id,
            "product_id": order.product_id,
            "product_description": product.description if product else None,
            "delivery_date": order.delivery_date,
            "address": order.address,
            "transport_type": order.transport_type.value,
            "province": order.province.value,  # Nowe pole
            "image": image_base64,
            "total_sum": product.price if product else None

        }), 200

    # --------------------- ADMIN RAPORTY ---------------------
    @app.route('/admin/report', methods=['GET'])
    @jwt_required()
    def generate_report():
        """
        Endpoint do generowania raportów przez admina.
        Przyjmuje daty początkową i końcową w formacie 'YYYY-MM-DD' jako query params.
        Zwraca:
            - całkowita liczba zamówień
            - łączna suma pieniędzy z zamówień
            - liczba zamówień z każdego województwa (jeśli > 0)

        Query Parameters:
            - start_date: "YYYY-MM-DD"
            - end_date: "YYYY-MM-DD"

        Example:
            GET /admin/report?start_date=2025-01-01&end_date=2025-12-31
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"msg": "Brak uprawnień"}), 403

        # Pobranie dat z query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({"msg": "Musisz podać datę początkową i końcową"}), 400

        # Parsowanie dat
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"msg": "Nieprawidłowy format daty. Użyj 'YYYY-MM-DD'"}), 400

        if start_date > end_date:
            return jsonify({"msg": "Data początkowa nie może być po dacie końcowej"}), 400

        # Filtracja zamówień w podanym zakresie dat
        # Zakładamy, że 'delivery_date' jest przechowywana jako string w formacie 'YYYY-MM-DD'
        # Porównywanie stringów działa poprawnie ze względu na format
        orders_query = Order.query.filter(
            Order.delivery_date >= start_date_str,
            Order.delivery_date <= end_date_str
        )

        # Obliczenie całkowitej liczby zamówień
        total_orders = orders_query.count()

        # Obliczenie łącznej sumy pieniędzy z zamówień przy użyciu funkcji SUM
        total_sum = db.session.query(func.sum(Product.price)).join(Order, Order.product_id == Product.id).filter(
            Order.delivery_date >= start_date_str,
            Order.delivery_date <= end_date_str
        ).scalar() or 0  # Używamy 'or 0', aby uniknąć None, gdy brak zamówień

        # Liczba zamówień z każdego województwa
        province_counts_query = db.session.query(Order.province, func.count(Order.id)).filter(
            Order.delivery_date >= start_date_str,
            Order.delivery_date <= end_date_str
        ).group_by(Order.province).all()

        # Przekształcenie wyników w słownik, filtrując województwa z liczbą zamówień > 0
        orders_per_province = {province.value: count for province, count in province_counts_query if count > 0}

        return jsonify({
            "total_orders": total_orders,
            "total_sum": total_sum,
            "orders_per_province": orders_per_province
        }), 200

    # --------------------- MOJE ZAMÓWIENIA ---------------------
    @app.route('/my_orders', methods=['GET'])
    @jwt_required()
    def my_orders():
        """
        Endpoint dla użytkownika do pobrania swoich zamówień.

        Input:
            - Header:
                Authorization: Bearer <JWT Token>

        Output JSON:
        [
            {
                "order_id": integer,
                "product_id": integer,
                "product_description": "string",
                "delivery_date": "YYYY-MM-DD",
                "address": "string",
                "transport_type": "string",
                "province": "string"
            },
            ...
        ]
        """
        current_user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=current_user_id).all()

        result = []
        for order in orders:
            product = Product.query.get(order.product_id)
            result.append({
                "order_id": order.id,
                "product_id": order.product_id,
                "product_description": product.description if product else None,
                "delivery_date": order.delivery_date,
                "address": order.address,
                "transport_type": order.transport_type.value,
                "province": order.province.value
            })

        return jsonify(result), 200

    # --------------------- USUŃ PRODUKT ---------------------
    @app.route('/product/<int:product_id>', methods=['DELETE'])
    @jwt_required()
    def delete_product(product_id):
        """
        Endpoint do usuwania produktu - wyłącznie przez admina.

        Input:
            - URL Parameter: product_id (integer)

        Header:
            Authorization: Bearer <JWT Token>
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"msg": "Brak uprawnień"}), 403

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Produkt nie istnieje"}), 404

        db.session.delete(product)
        db.session.commit()

        return jsonify({"msg": "Produkt usunięty"}), 200

    # --------------------- HANDLER BŁĘDÓW ---------------------
    @app.errorhandler(422)
    def handle_unprocessable_entity(err):
        return jsonify({"msg": "Nieprawidłowe dane w żądaniu", "error": str(err)}), 422

    return app
