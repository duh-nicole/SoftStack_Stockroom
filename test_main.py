from fastapi.testclient import TestClient
from main_controller import app

client = TestClient(app)

# Testing /products
def test_get_products_success():
    response = client.get("/products")
    assert response.status_code == 200


# Testing /product/{product_id} - Success
def test_get_product_id_success():
    response = client.get("/product/5")
    assert response.status_code == 200

# Testing /product/{product_id} - Fail
def test_get_product_id_not_found():
    response = client.get("/product/9999")
    assert response.status_code == 400
    actual_message = response.json()["detail"]["content"]
    assert actual_message == "Whoops! The product_id was not found."


# Testing /product/price - Success
def test_get_product_price_range_success():
    response = client.get("/products/price?min_price=14.00&max_price=16.00")
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
    response = client.get("/products/search?product_price=59.99")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Testing /products/search - Fail
def test_get_games_search_not_found():
    response = client.get("/products/search?product_price=0.05")
    assert response.status_code == 400
    actual_message = response.json()["detail"]["content"]
    assert actual_message == "Whoops! No games meet your type and price."


# Testing /products/mod
# Test - Validation Empty Strings - Fail
def test_update_product_invalid_data():
    payload = {
        "ID": 1,
        "Name": "",
        "Price": 19.99,
        "Type": "RPG"
    }
    response = client.post("/products/mod", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["content"] == "Product type or name cannot be left empty!"


# Test - Modification of Existing ID
def test_update_products_modify_existing():
    payload = {
        "ID": 3,
        "Name": "Minecraft Java Edition",
        "Price": 29.99,
        "Type": "Mojang"
    }
    response = client.post("/products/mod", json=payload)
    assert response.status_code == 200
    assert response.json() == "Product has been successfully modified!"



# Test - Adding New Product (New ID)
def test_update_products_add_new():
    payload = {
        "ID": 1234,
        "Name": "Sims 3",
        "Price": 29.99,
        "Type": "EA"
    }
    response = client.post("/products/mod", json=payload)
    assert response.status_code == 200
    assert response.json() == "Product has been successfully added!"