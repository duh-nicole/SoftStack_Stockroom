import pytest
from fastapi.testclient import TestClient
from main_controller import app
from init_db import reset_database

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """Runs once before all tests to reset and seed inventory.sqlite."""
    reset_database()


@pytest.fixture
def auth_token():
    """Log in and return a valid bearer token for use in tests."""
    response = client.post(
        "/auth/token",
        data={"username": "nicole", "password": "softstack123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# ==============================
# AUTH TESTS
# ==============================

def test_login_success():
    response = client.post(
        "/auth/token",
        data={"username": "nicole", "password": "softstack123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/auth/token",
        data={"username": "nicole", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_unknown_user():
    response = client.post(
        "/auth/token",
        data={"username": "ghost", "password": "whatever"}
    )
    assert response.status_code == 401


def test_unauthorized_access_no_token():
    response = client.get("/products")
    assert response.status_code == 401


def test_unauthorized_access_bad_token():
    response = client.get("/products", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401


# ==============================
# PRODUCT READ TESTS
# ==============================

def test_get_products_success(auth_headers):
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "FinalPrice" in response.json()[0]


def test_get_products_pagination(auth_headers):
    response = client.get("/products?limit=2&offset=0", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_get_product_by_id_success(auth_headers):
    # 1. Fetch current products to grab a real, existing ID
    products = client.get("/products?limit=1", headers=auth_headers).json()

    # 2. If DB is empty, add one on the fly first
    if not products:
        client.post(
            "/products/mod",
            json={"Name": "Test Item", "Price": 5.00, "Type": "Merch"},
            headers=auth_headers
        )
        products = client.get("/products?limit=1", headers=auth_headers).json()

    target_id = products[0]["ID"]

    # 3. Request by the confirmed valid ID
    response = client.get(f"/product/{target_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ID"] == target_id


def test_get_product_by_id_not_found(auth_headers):
    response = client.get("/product/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_price_range_success(auth_headers):
    response = client.get("/products/price?min_price=3.00&max_price=17.00", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_price_range_empty_is_valid(auth_headers):
    """No matches should return 200 + empty list, not an error."""
    response = client.get("/products/price?min_price=9999&max_price=10000", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_price_range_invalid_bounds(auth_headers):
    response = client.get("/products/price?min_price=50&max_price=10", headers=auth_headers)
    assert response.status_code == 400


def test_search_products_by_price(auth_headers):
    response = client.get("/products/search?product_price=4.50", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_products_no_match(auth_headers):
    response = client.get("/products/search?product_price=0.01", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


# ==============================
# PRODUCT WRITE TESTS
# ==============================

def test_add_new_product(auth_headers):
    payload = {"Name": "Test Espresso Pod", "Price": 9.99, "Type": "Coffee Beans"}
    response = client.post("/products/mod", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "added" in response.json()["content"].lower()


def test_update_existing_product(auth_headers):
    add_response = client.post(
        "/products/mod",
        json={"Name": "Temp Product", "Price": 5.00, "Type": "Merch"},
        headers=auth_headers
    )
    new_id = client.get("/products?limit=1&offset=0", headers=auth_headers).json()[0]["ID"]

    payload = {"ID": new_id, "Name": "Updated Name", "Price": 6.00, "Type": "Merch"}
    response = client.post("/products/mod", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "modified" in response.json()["content"].lower()


def test_add_product_empty_name_fails(auth_headers):
    payload = {"Name": "", "Price": 19.99, "Type": "RPG"}
    response = client.post("/products/mod", json=payload, headers=auth_headers)
    assert response.status_code == 400


def test_add_product_negative_price_fails(auth_headers):
    payload = {"Name": "Broken Item", "Price": -5.00, "Type": "Merch"}
    response = client.post("/products/mod", json=payload, headers=auth_headers)
    assert response.status_code == 422  # Pydantic validation, not our own 400


# ==============================
# BULK OPERATIONS TESTS
# ==============================

def test_bulk_save_products(auth_headers):
    payload = {
        "products": [
            {"Name": "Bulk Item A", "Price": 3.00, "Type": "Merch"},
            {"Name": "Bulk Item B", "Price": 4.00, "Type": "Merch"},
        ]
    }
    response = client.post("/products/bulk-save", json=payload, headers=auth_headers)
    assert response.status_code == 200


def test_bulk_delete_products(auth_headers):
    # Add one first so we know an ID exists to delete
    client.post(
        "/products/mod",
        json={"Name": "Delete Me", "Price": 1.00, "Type": "Merch"},
        headers=auth_headers
    )
    products = client.get("/products?limit=1", headers=auth_headers).json()
    target_id = products[0]["ID"]

    response = client.request(
        "DELETE",
        "/products/bulk-delete",
        json={"product_ids": [target_id]},
        headers=auth_headers
    )
    assert response.status_code == 200


def test_bulk_delete_no_matches(auth_headers):
    response = client.request(
        "DELETE",
        "/products/bulk-delete",
        json={"product_ids": [999999]},
        headers=auth_headers
    )
    assert response.status_code == 200


""" Thanks for using SoftStack Studios! """
