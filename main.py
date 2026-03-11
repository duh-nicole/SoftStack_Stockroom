from fastapi import FastAPI
from typing import Union
app = FastAPI()

Products = [{'Name': 'Apple', 'Price': 4.99, 'Type': 'Fruit'},
            {'Name': 'Orange', 'Price': 8.99, 'Type': 'Fruit'},
            {'Name': 'Tomato', 'Price': 3.99, 'Type': 'Fruit'},
            {'Name': 'Cabbage', 'Price': 1.99, 'Type': 'Vegetable'},
            {'Name': 'Potato', 'Price': 2.50, 'Type': 'Vegetable'}
]

@app.get("/product")
def get_products(product_price: float, product_type: Union[str, None] = None, product_name: Union[str, None] = None):
    # Making the filter for price
    results = [p for p in Products if p['Price'] == product_price]
    # Adding filter for type
    if product_type:
        results = [p for p in results if p['Type'].lower() == product_type.lower()]
    # And another filter for name, if provided
    if product_name:
        results = [p for p in results if p['Name'].lower() == product_name.lower()]

    return results

@app.get("/product/price")
def get_all_products_price_range(min_price: float, max_price: float):
    results = [p for p in Products if min_price < p['Price'] < max_price]
    return results

