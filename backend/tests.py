# tests.py

import pytest
import os
from app import create_app
from db_models import db, User

@pytest.fixture
def test_app():
    """
    Fixture tworząca instancję aplikacji Flask z in-memory SQLite
    i tworząca tabele w bazie przed testami.
    """
    # Wskazujemy bazę w pamięci
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
    }

    # Tworzymy aplikację w trybie testowym i w kontekście
    app = create_app(test_config=test_config)
    with app.app_context():
        db.create_all()
        yield app
        # Po zakończeniu testów: usuwamy tabele (opcjonalnie)
        db.drop_all()

@pytest.fixture
def client(test_app):
    """
    Fixture zwracająca testowego klienta, za pomocą którego
    będziemy wykonywać zapytania HTTP.
    """
    return test_app.test_client()


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200


def test_register_success(client):
    response = client.post('/register', json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201


def test_register_existing_user(client):
    """
    Najpierw rejestrujemy użytkownika, potem ponawiamy rejestrację
    z tymi samymi danymi -> 400.
    """
    _ = client.post('/register', json={
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "testpassword"
    })
    response = client.post('/register', json={
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 400


def test_register_invalid_data(client):
    response = client.post('/register', json={
        "email": "noUsername@example.com"
    })
    assert response.status_code == 400


def test_login_success(client):
    """
    Najpierw rejestrujemy usera, żeby istniał w bazie,
    potem testujemy logowanie.
    """
    register_resp = client.post('/register', json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpassword"
    })
    assert register_resp.status_code == 201

    response = client.post('/login', json={
        "email": "login@example.com",
        "password": "loginpassword"
    })
    assert response.status_code == 200


def test_login_invalid_password(client):
    """
    Najpierw rejestrujemy usera, potem próbujemy się zalogować z błędnym hasłem.
    """
    _ = client.post('/register', json={
        "username": "wrongpass",
        "email": "wrongpass@example.com",
        "password": "correctpass"
    })
    response = client.post('/login', json={
        "email": "wrongpass@example.com",
        "password": "badpass"
    })
    assert response.status_code == 401


def test_login_invalid_data(client):
    """
    Brak hasła w żądaniu -> 400.
    """
    _ = client.post('/register', json={
        "username": "noPass",
        "email": "noPass@example.com",
        "password": "somePass"
    })
    response = client.post('/login', json={
        "email": "noPass@example.com"
        # brak password
    })
    assert response.status_code == 400

def test_admin_login_success(client):
    """
    Poprawne logowanie jako admin z danymi z .env:
    ADMIN_USERNAME=admin, ADMIN_PASSWORD=secret
    Oczekujemy statusu 200 i zwrotu access_token.
    """
    response = client.post('/login', json={
        "email": "admin@example.com",
        "password": "secret"
    })
    print('dupa')
    print(response.data)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


def test_admin_login_invalid_data(client):
    """
    Próba logowania admina z nieprawidłowymi danymi.
    Oczekujemy statusu 401.
    """
    response = client.post('/login', json={
        "email": "admin@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401


def test_add_product_no_auth(client):
    """
    Próba dodania produktu bez tokena JWT.
    Oczekujemy statusu 401 (Unauthorized), bo wymagana jest autoryzacja.
    """
    response = client.post('/product', json={
        "description": "Cebula dymka",
        "price": 15.0
    })
    assert response.status_code == 401


def test_add_product_not_admin(client):
    """
    Próba dodania produktu za pomocą konta zwykłego użytkownika.
    Oczekujemy statusu 403 (Forbidden), bo tylko admin może dodać produkt.
    """
    # Najpierw rejestrujemy zwykłego użytkownika
    register_resp = client.post('/register', json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password1"
    })
    assert register_resp.status_code == 201

    # Logujemy się jako zwykły użytkownik
    login_resp = client.post('/login', json={
        "email": "user1@example.com",
        "password": "password1"
    })
    assert login_resp.status_code == 200
    user_data = login_resp.get_json()
    user_token = user_data["access_token"]

    # Próbujemy dodać produkt
    response = client.post('/product',
                           json={
                               "description": "Pomidory gruntowe",
                               "price": 10.5
                           },
                           headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403


def test_add_product_success(client):
    """
    Dodanie produktu przez zalogowanego admina.
    Oczekujemy statusu 201 i zwrotu product_id.
    """
    # Logowanie admina
    admin_resp = client.post('/login', json={
        "email": "admin@example.com",
        "password": "secret"
    })
    assert admin_resp.status_code == 200
    admin_data = admin_resp.get_json()
    admin_token = admin_data["access_token"]

    # Dodajemy produkt
    response = client.post('/product',
                           json={
                               "description": "Marchew jadalna",
                               "price": 9.99
                           },
                           headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    data = response.get_json()
    assert "product_id" in data


def test_get_product(client):
    """
    Pobranie istniejącego produktu.
    Zakładamy, że w poprzednim teście produkt został dodany.
    Oczekujemy statusu 200 oraz danych JSON z kluczami: id, description, price, image.
    """
    # Najpierw zaloguj admina i dodaj produkt (jeśli chcemy być niezależni od poprzedniego testu):
    admin_resp = client.post('/login', json={
        "email": "admin@example.com",
        "password": "secret"
    })
    admin_token = admin_resp.get_json()["access_token"]

    add_resp = client.post('/product',
                           json={
                               "description": "Ziemniaki jadalne",
                               "price": 5.5
                           },
                           headers={"Authorization": f"Bearer {admin_token}"})
    product_id = add_resp.get_json()["product_id"]

    # Pobierz dodany produkt
    response = client.get(f'/product/{product_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == product_id
    assert data["description"] == "Ziemniaki jadalne"
    assert data["price"] == 5.5
    # image może być None lub string base64
    assert "image" in data


def test_get_nonexistent_product(client):
    """
    Próba pobrania produktu o ID, którego nie ma w bazie.
    Oczekujemy statusu 404.
    """
    response = client.get('/product/999999')  # zakładamy, że taki nie istnieje
    assert response.status_code == 404




def test_get_all_products(client):
    """
    Test sprawdzający, czy endpoint /products zwraca listę produktów (status 200).
    Wcześniej tworzymy parę produktów (przez admina) i sprawdzamy,
    czy pojawiają się w zwróconej liście.
    """
    # 1. Zaloguj jako admin
    admin_resp = client.post('/login', json={
        "email": "admin@example.com",
        "password": "secret"
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # 2. Dodaj kilka produktów
    products_to_add = [
        {"description": "Ziemniaki jadalne", "price": 5.5},
        {"description": "Marchew jadalna", "price": 9.99}
    ]
    for p in products_to_add:
        add_resp = client.post(
            '/product',
            json=p,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert add_resp.status_code == 201

    # 3. Wywołaj endpoint /products
    get_resp = client.get('/products')
    assert get_resp.status_code == 200

    # 4. Sprawdź, czy lista produktów zawiera nasze dodane produkty
    data = get_resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2  # powinno być co najmniej tyle, ile dodaliśmy

    # Możemy sprawdzić, czy opis i cena naszych produktów jest w odpowiedzi
    descriptions = [item['description'] for item in data]
    prices = [item['price'] for item in data]

    assert "Ziemniaki jadalne" in descriptions
    assert 5.5 in prices
    assert "Marchew jadalna" in descriptions
    assert 9.99 in prices




def test_create_order_success(client):
    """
    Scenariusz:
      1. Zaloguj admina i stwórz produkt (product_id).
      2. Zarejestruj i zaloguj zwykłego użytkownika (user_token).
      3. Użytkownik tworzy zamówienie na istniejący produkt.
      4. Oczekujemy kodu 201 i zwrotu order_id.
    """
    # 1. Zaloguj admina
    admin_resp = client.post('/login', json={
        "email": "admin@example.com",
        "password": "secret"
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # 2. Stwórz produkt (przez admina)
    product_resp = client.post('/product',
                               json={"description": "Ziemniaki", "price": 10.0},
                               headers={"Authorization": f"Bearer {admin_token}"})
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["product_id"]

    # 3. Zarejestruj użytkownika i zaloguj
    register_resp = client.post('/register', json={
        "username": "user_order",
        "email": "user_order@example.com",
        "password": "abc123"
    })
    assert register_resp.status_code == 201

    login_resp = client.post('/login', json={
        "email": "user_order@example.com",
        "password": "abc123"
    })
    assert login_resp.status_code == 200
    user_token = login_resp.get_json()["access_token"]

    # 4. Użytkownik tworzy zamówienie
    order_resp = client.post('/order',
                             json={
                                 "product_id": product_id,
                                 "delivery_date": "2025-05-20",
                                 "address": "ul. Rolna 10",
                                 "transport_type": "TRUCK",
                                 "province": "mazowieckie"
                             },
                        headers={"Authorization": f"Bearer {user_token}"})


    assert order_resp.status_code == 201
    order_data = order_resp.get_json()
    assert "order_id" in order_data


def test_create_order_no_jwt(client):
    """
    Próba tworzenia zamówienia bez tokena JWT -> 401 (Unauthorized),
    bo używamy dekoratora @jwt_required().
    """
    order_resp = client.post('/order', json={
        "product_id": 1,
        "delivery_date": "2025-05-20",
        "address": "ul. Rolna 10",
        "transport_type": "truck"
    })
    assert order_resp.status_code == 401


def test_create_order_product_not_found(client):
    """
    Próba zamówienia produktu, który nie istnieje (np. ID=999999).
    Oczekujemy 404.
    """
    # Zarejestruj i zaloguj użytkownika, żeby mieć token
    register_resp = client.post('/register', json={
        "username": "user_unknown_product",
        "email": "user_unknown_product@example.com",
        "password": "abc123"
    })
    assert register_resp.status_code == 201

    login_resp = client.post('/login', json={
        "email": "user_unknown_product@example.com",
        "password": "abc123"
    })
    assert login_resp.status_code == 200
    user_token = login_resp.get_json()["access_token"]

    # Próba utworzenia zamówienia na nieistniejący product_id = 999999
    order_resp = client.post('/order',
                             json={
                                 "product_id": 999999,
                                 "delivery_date": "2025-05-20",
                                 "address": "ul. Rolna 10",
                                 "transport_type": "truck",
                                 "province": "mazowieckie"
                             },
                             headers={"Authorization": f"Bearer {user_token}"})
    assert order_resp.status_code == 404


def test_create_order_invalid_transport(client):
    """
    Próba zamówienia z niepoprawnym rodzajem transportu.
    Oczekujemy 400 i komunikatu o dozwolonych wartościach enuma.
    """
    # Najpierw utwórzmy produkt przez admina
    admin_resp = client.post('/login', json={
        "email": "admin@example.com",
        "password": "secret"
    })
    admin_token = admin_resp.get_json()["access_token"]

    product_resp = client.post('/product',
                               json={"description": "Marchew", "price": 5.0},
                               headers={"Authorization": f"Bearer {admin_token}"})
    product_id = product_resp.get_json()["product_id"]

    # Zarejestruj i zaloguj użytkownika
    client.post('/register', json={
        "username": "user_invalid_transport",
        "email": "user_invalid_transport@example.com",
        "password": "abc123"
    })
    login_resp = client.post('/login', json={
        "email": "user_invalid_transport@example.com",
        "password": "abc123"
    })
    user_token = login_resp.get_json()["access_token"]

    # Ustawiamy nieprawidłowy transport_type
    order_resp = client.post('/order',
                             json={
                                 "product_id": product_id,
                                 "delivery_date": "2025-05-20",
                                 "address": "ul. Rolna 10",
                                 "transport_type": "teleporter"  # nie ma w Enum
                             },
                             headers={"Authorization": f"Bearer {user_token}"})
    assert order_resp.status_code == 400
    data = order_resp.get_json()
    assert "Niekompletne dane zamówienia" in data.get("msg", "")

def test_edit_product_success(client):
    """
    Scenariusz:
      1. Logowanie admina.
      2. Dodanie produktu.
      3. Edycja produktu przez admina.
      4. Sprawdzenie, czy produkt został poprawnie zaktualizowany.
    """
    # 1. Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # 2. Dodanie produktu
    product_resp = client.post('/product',
                               json={"description": "Ziemniaki", "price": 10.0},
                               headers={"Authorization": f"Bearer {admin_token}"})
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["product_id"]

    # 3. Edycja produktu
    edit_resp = client.put(f'/product/{product_id}',
                           json={
                               "description": "Ziemniaki ekologiczne",
                               "price": 12.5,
                               "image": ""  # Usunięcie obrazu, jeśli był
                           },
                           headers={"Authorization": f"Bearer {admin_token}"})
    assert edit_resp.status_code == 200
    data = edit_resp.get_json()
    assert data["msg"] == "Produkt zaktualizowany"

    # 4. Sprawdzenie, czy produkt został zaktualizowany
    get_resp = client.get(f'/product/{product_id}')
    assert get_resp.status_code == 200
    product_data = get_resp.get_json()
    assert product_data["description"] == "Ziemniaki ekologiczne"
    assert product_data["price"] == 12.5
    assert product_data["image"] is None  # Obraz został usunięty

def test_edit_product_no_auth(client):
    """
    Próba edycji produktu bez tokena JWT -> 401.
    """
    edit_resp = client.put('/product/1',
                           json={
                               "description": "Testowanie bez autoryzacji",
                               "price": 15.0
                           })
    assert edit_resp.status_code == 401



def test_generate_report_success(client):
    """
    Scenariusz:
      1. Zaloguj admina.
      2. Dodaj kilka produktów.
      3. Dodaj kilka zamówień w różnych województwach i datach.
      4. Wygeneruj raport dla określonego zakresu dat.
      5. Sprawdź poprawność zwróconych danych.
    """
    # 1. Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # 2. Dodanie produktów
    product_ids = []
    products = [
        {"description": "Produkt A", "price": 100.0},
        {"description": "Produkt B", "price": 200.0},
        {"description": "Produkt C", "price": 300.0},
    ]
    for product in products:
        resp = client.post('/product',
                           json=product,
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201
        product_ids.append(resp.get_json()["product_id"])

    # 3. Dodanie zamówień
    # Rejestracja i logowanie użytkowników
    users = [
        {"username": "user1", "email": "user1@example.com", "password": "pass1"},
        {"username": "user2", "email": "user2@example.com", "password": "pass2"},
    ]
    user_tokens = []
    for user in users:
        register_resp = client.post('/register', json=user)
        assert register_resp.status_code == 201
        login_resp = client.post('/login', json={
            "email": user["email"],
            "password": user["password"]
        })
        assert login_resp.status_code == 200
        user_tokens.append(login_resp.get_json()["access_token"])

    # Dodanie zamówień przez użytkowników
    orders = [
        {
            "product_id": product_ids[0],
            "delivery_date": "2025-05-20",
            "address": "ul. Rolna 10, 00-000 Warszawa",
            "transport_type": "TRUCK",
            "province": "mazowieckie"
        },
        {
            "product_id": product_ids[1],
            "delivery_date": "2025-06-15",
            "address": "ul. Leśna 5, 30-000 Kraków",
            "transport_type": "COURIER",
            "province": "małopolskie"
        },
        {
            "product_id": product_ids[2],
            "delivery_date": "2025-07-10",
            "address": "ul. Miejska 12, 20-000 Lublin",
            "transport_type": "PICKUP",
            "province": "lubelskie"
        },
        {
            "product_id": product_ids[0],
            "delivery_date": "2025-05-25",
            "address": "ul. Wiejska 8, 40-000 Katowice",
            "transport_type": "TRUCK",
            "province": "śląskie"
        },
    ]

    for i, order in enumerate(orders):
        resp = client.post('/order',
                           json=order,
                           headers={"Authorization": f"Bearer {user_tokens[i % len(user_tokens)]}"})
        assert resp.status_code == 201

    # 4. Generowanie raportu dla zakresu dat
    report_start_date = "2025-05-01"
    report_end_date = "2025-06-30"
    report_resp = client.get('/admin/report',
                             query_string={
                                 "start_date": report_start_date,
                                 "end_date": report_end_date
                             },
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert report_resp.status_code == 200
    report_data = report_resp.get_json()

    # 5. Sprawdzenie poprawności danych raportu
    assert report_data["total_orders"] == 3  # Zamówienia z maja i czerwca
    assert report_data["total_sum"] == 100.0 + 200.0 + 100.0  # Produkt A + B + A
    expected_provinces = {
        "mazowieckie": 1,
        "małopolskie": 1,
        "śląskie": 1
    }
    assert report_data["orders_per_province"] == expected_provinces

def test_generate_report_non_admin(client):
    """
    Sprawdza, czy użytkownik niebędący adminem nie może generować raportów.
    """
    # Rejestracja i logowanie zwykłego użytkownika
    user = {"username": "regular_user", "email": "regular@example.com", "password": "userpass"}
    register_resp = client.post('/register', json=user)
    assert register_resp.status_code == 201
    login_resp = client.post('/login', json={
        "email": user["email"],
        "password": user["password"]
    })
    assert login_resp.status_code == 200
    user_token = login_resp.get_json()["access_token"]

    # Próba generowania raportu przez zwykłego użytkownika
    report_resp = client.get('/admin/report',
                             query_string={
                                 "start_date": "2025-05-01",
                                 "end_date": "2025-06-30"
                             },
                             headers={"Authorization": f"Bearer {user_token}"})
    assert report_resp.status_code == 403
    data = report_resp.get_json()
    assert "Brak uprawnień" in data["msg"]

def test_generate_report_invalid_date_format(client):
    """
    Próba generowania raportu z nieprawidłowym formatem daty.
    """
    # Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # Próba generowania raportu z nieprawidłowym formatem dat
    report_resp = client.get('/admin/report',
                             query_string={
                                 "start_date": "20-05-2025",  # Nieprawidłowy format
                                 "end_date": "2025/06/30"     # Nieprawidłowy format
                             },
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert report_resp.status_code == 400
    data = report_resp.get_json()
    assert "Nieprawidłowy format daty" in data["msg"]

def test_generate_report_start_date_after_end_date(client):
    """
    Próba generowania raportu, gdy data początkowa jest po dacie końcowej.
    """
    # Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # Próba generowania raportu z datą początkową po dacie końcowej
    report_resp = client.get('/admin/report',
                             query_string={
                                 "start_date": "2025-07-01",
                                 "end_date": "2025-06-30"
                             },
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert report_resp.status_code == 400
    data = report_resp.get_json()
    assert "Data początkowa nie może być po dacie końcowej" in data["msg"]

def test_generate_report_missing_parameters(client):
    """
    Próba generowania raportu bez podania wymaganych parametrów.
    """
    # Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # Próba generowania raportu bez daty początkowej
    report_resp = client.get('/admin/report',
                             query_string={
                                 "end_date": "2025-06-30"
                             },
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert report_resp.status_code == 400
    data = report_resp.get_json()
    assert "Musisz podać datę początkową i końcową" in data["msg"]

    # Próba generowania raportu bez daty końcowej
    report_resp = client.get('/admin/report',
                             query_string={
                                 "start_date": "2025-05-01"
                             },
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert report_resp.status_code == 400
    data = report_resp.get_json()
    assert "Musisz podać datę początkową i końcową" in data["msg"]

def test_generate_report_no_orders(client):
    """
    Generowanie raportu w okresie, w którym nie ma żadnych zamówień.
    """
    # Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # Generowanie raportu dla okresu bez zamówień
    report_resp = client.get('/admin/report',
                             query_string={
                                 "start_date": "2024-01-01",
                                 "end_date": "2024-12-31"
                             },
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert report_resp.status_code == 200
    report_data = report_resp.get_json()
    assert report_data["total_orders"] == 0
    assert report_data["total_sum"] == 0
    assert report_data["orders_per_province"] == {}


def test_my_orders_success(client):
    """
    Scenariusz:
      1. Admin loguje się i dodaje produkt.
      2. Użytkownik rejestruje się, loguje i tworzy kilka zamówień.
      3. Użytkownik pobiera swoje zamówienia.
      4. Sprawdza poprawność zwróconych danych.
    """
    # 1. Logowanie admina i dodanie produktu
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    product_resp = client.post('/product',
                               json={
                                   "description": "Produkt Testowy",
                                   "price": 150.0
                               },
                               headers={"Authorization": f"Bearer {admin_token}"})
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["product_id"]

    # 2. Rejestracja i logowanie użytkownika
    user_data = {
        "username": "user_test",
        "email": "user_test@example.com",
        "password": "password123"
    }
    register_resp = client.post('/register', json=user_data)
    assert register_resp.status_code == 201

    login_resp = client.post('/login', json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert login_resp.status_code == 200
    user_token = login_resp.get_json()["access_token"]

    # 3. Tworzenie zamówień
    orders = [
        {
            "product_id": product_id,
            "delivery_date": "2025-08-10",
            "address": "ul. Testowa 1, 00-001 Warszawa",
            "transport_type": "COURIER",
            "province": "mazowieckie"
        },
        {
            "product_id": product_id,
            "delivery_date": "2025-09-15",
            "address": "ul. Testowa 2, 30-002 Kraków",
            "transport_type": "PICKUP",
            "province": "małopolskie"
        },
    ]

    for order in orders:
        order_resp = client.post('/order',
                                 json=order,
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert order_resp.status_code == 201

    # 4. Pobranie zamówień przez użytkownika
    my_orders_resp = client.get('/my_orders',
                                 headers={"Authorization": f"Bearer {user_token}"})
    assert my_orders_resp.status_code == 200
    my_orders = my_orders_resp.get_json()
    assert len(my_orders) == 2

    for order in my_orders:
        assert "order_id" in order
        assert "product_id" in order
        assert "product_description" in order
        assert "delivery_date" in order
        assert "address" in order
        assert "transport_type" in order
        assert "province" in order

def test_my_orders_no_auth(client):
    """
    Próba pobrania zamówień bez tokena JWT -> 401 (Unauthorized).
    """
    my_orders_resp = client.get('/my_orders')
    assert my_orders_resp.status_code == 401

def test_my_orders_empty(client):
    """
    Pobranie zamówień, gdy użytkownik nie ma żadnych zamówień.
    """
    # Rejestracja i logowanie użytkownika
    user_data = {
        "username": "user_empty",
        "email": "user_empty@example.com",
        "password": "password123"
    }
    register_resp = client.post('/register', json=user_data)
    assert register_resp.status_code == 201

    login_resp = client.post('/login', json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert login_resp.status_code == 200
    user_token = login_resp.get_json()["access_token"]

    # Pobranie zamówień przez użytkownika bez zamówień
    my_orders_resp = client.get('/my_orders',
                                 headers={"Authorization": f"Bearer {user_token}"})
    assert my_orders_resp.status_code == 200
    my_orders = my_orders_resp.get_json()
    assert my_orders == []

# --------------------- TESTY USUŃ PRODUKT ---------------------

def test_delete_product_success(client):
    """
    Scenariusz:
      1. Admin loguje się i dodaje produkt.
      2. Admin usuwa produkt.
      3. Sprawdza, czy produkt został usunięty.
    """
    # 1. Logowanie admina i dodanie produktu
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    product_resp = client.post('/product',
                               json={
                                   "description": "Produkt Do Usunięcia",
                                   "price": 250.0
                               },
                               headers={"Authorization": f"Bearer {admin_token}"})
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["product_id"]

    # 2. Usunięcie produktu przez admina
    delete_resp = client.delete(f'/product/{product_id}',
                                headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_resp.status_code == 200
    assert delete_resp.get_json()["msg"] == "Produkt usunięty"

    # 3. Sprawdzenie, czy produkt został usunięty
    get_resp = client.get(f'/product/{product_id}')
    assert get_resp.status_code == 404
    assert get_resp.get_json()["msg"] == "Produkt nie istnieje"

def test_delete_product_no_auth(client):
    """
    Próba usunięcia produktu bez tokena JWT -> 401 (Unauthorized).
    """
    delete_resp = client.delete('/product/1')
    assert delete_resp.status_code == 401

def test_delete_product_not_admin(client):
    """
    Próba usunięcia produktu przez użytkownika niebędącego adminem -> 403 (Forbidden).
    """
    # 1. Admin loguje się i dodaje produkt
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    product_resp = client.post('/product',
                               json={
                                   "description": "Produkt Testowy",
                                   "price": 300.0
                               },
                               headers={"Authorization": f"Bearer {admin_token}"})
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["product_id"]

    # 2. Rejestracja i logowanie zwykłego użytkownika
    user_data = {
        "username": "user_non_admin",
        "email": "user_non_admin@example.com",
        "password": "password123"
    }
    register_resp = client.post('/register', json=user_data)
    assert register_resp.status_code == 201

    login_resp = client.post('/login', json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert login_resp.status_code == 200
    user_token = login_resp.get_json()["access_token"]

    # 3. Próba usunięcia produktu przez zwykłego użytkownika
    delete_resp = client.delete(f'/product/{product_id}',
                                headers={"Authorization": f"Bearer {user_token}"})
    assert delete_resp.status_code == 403
    assert delete_resp.get_json()["msg"] == "Brak uprawnień"

def test_delete_product_not_found(client):
    """
    Próba usunięcia nieistniejącego produktu -> 404 (Not Found).
    """
    # Logowanie admina
    admin_email = "admin@example.com"
    admin_password = os.getenv('ADMIN_PASSWORD', 'secret')
    admin_resp = client.post('/login', json={
        "email": admin_email,
        "password": admin_password
    })
    assert admin_resp.status_code == 200
    admin_token = admin_resp.get_json()["access_token"]

    # Próba usunięcia produktu o nieistniejącym ID
    delete_resp = client.delete('/product/999999',
                                headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_resp.status_code == 404
    assert delete_resp.get_json()["msg"] == "Produkt nie istnieje"