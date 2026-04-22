from fastapi.testclient import TestClient
from main_controller import app

client = TestClient(app)

# Testing /products
def test_get_products_success():
    response = client.get("/products")
    assert response.status_code == 200


# Testing /product/{product_id} - Success
def test_get_product_id_success():
    response = client.get("/product/1")
    assert response.status_code == 200

# Testing /product/{product_id} Fail - 400 Bad Request
def test_get_product_id_not_found():
    response = client.get("/product/9999")
    assert response.status_code == 400
    actual_message = response.json()["detail"]["content"]
    assert actual_message == "Whoops! The product_id was not found."


# Testing /product/price - Success
def test_get_product_price_range_success():
    response = client.get("/products/price?min_price=10.0&max_price=100.0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Testing /product/price - Fail
def test_get_product_price_range_not_found():
    response = client.get("/products/price?min_price=999.99&max_price=1000.00")
    assert response.status_code == 400
    actual_message = response.json()["detail"]["content"]
    assert actual_message == "Whoops! No products within the specified range."


# Testing /products/search - Success
def test_get_games_search_success():
    response = client.get("/games")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Testing /products/search - Fail
def test_get_games_search_not_found():
    response = client.get("/games")
    assert response.status_code == 400
    actual_message = response.json()["detail"]["content"]
    assert actual_message == "Whoops! No games meet your type and price."

# Testing /products/mod - Success
