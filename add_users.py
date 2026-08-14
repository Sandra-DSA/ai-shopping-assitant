#
# # SPDX-License-Identifier: Apache-2.0
# # Copyright (c) 2026 Data Science Academy Pvt. Ltd. (https://www.datascience.one)
# ##
import requests
from requests.auth import HTTPBasicAuth


# =========================
# CONFIG
# =========================
WP_BASE_URL = "http://localhost:8080"

# WordPress admin username + Application Password
WP_USERNAME = "admin"
WP_APP_PASSWORD = "FbX8 LzHb evPX ZjW2 75dY 9Lrh"

# WooCommerce API keys
WC_CONSUMER_KEY = "ck_2d5b355be4f971c7da85e816d47a544d604e8f45"
WC_CONSUMER_SECRET = "cs_f0df2f6ee660bf2c37b7eb796c570b0c4e9de059"


# =========================
# WORDPRESS USER FUNCTIONS
# =========================
def create_wp_user(username: str, email: str, password: str, role: str = "subscriber") -> dict:
    """
    Create a WordPress user using WP REST API.
    """
    url = f"{WP_BASE_URL}/wp-json/wp/v2/users"
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "roles": [role],
    }

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )

    try:
        data = response.json()
    except Exception:
        data = {"raw_text": response.text}

    if response.status_code in (200, 201):
        print(f"✅ User created: {username}")
        return data
    else:
        print(f"❌ Failed to create user: {username}")
        print(f"Status: {response.status_code}")
        print(data)
        return data


# =========================
# WOOCOMMERCE PRODUCT FUNCTIONS
# =========================
def create_product(
    name: str,
    regular_price: str,
    description: str = "",
    short_description: str = "",
    sku: str | None = None,
    stock_quantity: int = 10,
    categories: list[int] | None = None,
) -> dict:
    """
    Create a WooCommerce product using WC REST API.
    """
    url = f"{WP_BASE_URL}/wp-json/wc/v3/products"

    payload = {
        "name": name,
        "type": "simple",
        "regular_price": regular_price,
        "description": description,
        "short_description": short_description,
        "manage_stock": True,
        "stock_quantity": stock_quantity,
    }

    if sku:
        payload["sku"] = sku

    if categories:
        payload["categories"] = [{"id": cat_id} for cat_id in categories]

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET),
        timeout=30,
    )

    try:
        data = response.json()
    except Exception:
        data = {"raw_text": response.text}

    if response.status_code in (200, 201):
        print(f"✅ Product created: {name}")
        return data
    else:
        print(f"❌ Failed to create product: {name}")
        print(f"Status: {response.status_code}")
        print(data)
        return data


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    # Create a few users
    users_to_create = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "John@12345",
            "role": "subscriber",
        },
        {
            "username": "sarah_editor",
            "email": "sarah@example.com",
            "password": "Sarah@12345",
            "role": "editor",
        },
        {
            "username": "mike_customer",
            "email": "mike@example.com",
            "password": "Mike@12345",
            "role": "customer",   # useful if WooCommerce role exists
        },
    ]

    print("\n=== Creating WordPress Users ===")
    for user in users_to_create:
        create_wp_user(
            username=user["username"],
            email=user["email"],
            password=user["password"],
            role=user["role"],
        )

    # Create a few WooCommerce products
    products_to_create = [
        {
            "name": "Blue T-Shirt",
            "regular_price": "499",
            "description": "Comfortable blue cotton T-shirt.",
            "short_description": "Blue cotton T-shirt",
            "sku": "TSHIRT-BLUE-001",
            "stock_quantity": 25,
        },
        {
            "name": "Running Shoes",
            "regular_price": "2499",
            "description": "Lightweight running shoes for daily workouts.",
            "short_description": "Lightweight running shoes",
            "sku": "SHOE-RUN-001",
            "stock_quantity": 12,
        },
        {
            "name": "Coffee Mug",
            "regular_price": "299",
            "description": "Ceramic mug for coffee and tea.",
            "short_description": "Ceramic coffee mug",
            "sku": "MUG-001",
            "stock_quantity": 40,
        },
    ]

    print("\n=== Creating WooCommerce Products ===")
    for product in products_to_create:
        create_product(
            name=product["name"],
            regular_price=product["regular_price"],
            description=product["description"],
            short_description=product["short_description"],
            sku=product["sku"],
            stock_quantity=product["stock_quantity"],
        )
