from fastapi.testclient import TestClient
from main_controller import app

client = TestClient(app)

# Testing /products
def test_get_products_success():
    response = client.get("/products")
    assert response.status_code == 200

# Testing /product/{product_id} Success
def test_get_product_id_success():
    response = client.get("/product/1")
    assert response.status_code == 200

# Testing /product/{product_id} Fail - 400 Bad Request
def test_get_product_id_not_found():
    response = client.get("/product/9999")
    assert response.status_code == 400
    assert response.json()["detail"]["content"] == "Whoops! The product_id was not found."

