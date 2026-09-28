# TechGear Store

A locally run Django storefront for computer gear, peripherals and accessories. The interface is built with Django templates, Bootstrap 5, custom CSS and small vanilla JavaScript enhancements. SQLite is used for development.

## Features

- Responsive homepage, product catalog, category pages and product detail pages
- Search by name, brand, category or description; filter by brand and price; sort and paginate
- User registration, login, logout and profile editing using Django authentication
- Session-based cart with quantity and stock validation
- Authenticated checkout, order confirmation, order history and private order details
- Atomic stock reduction at checkout, Django admin for catalog and order management
- Seed command for 37 realistic sample products across 10 categories
- Product-specific images sourced from online manufacturer and retailer listings, cached locally for reliable display

## Technology stack

Python 3.10+, Django 5.2, SQLite, HTML, CSS, Bootstrap 5 and vanilla JavaScript.

## Project structure

```text
techgear/       Django configuration and URL routing
accounts/       Registration, login and profile
products/       Catalog models, views, admin and sample data command
cart/           Session cart and cart views
orders/         Checkout, order models, history and admin
templates/      Shared layout and page templates
static/         Custom CSS and JavaScript
```

## Installation and local run

From the project directory:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows Command Prompt: .venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations products orders
python manage.py migrate
python manage.py seed_store
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin is at `http://127.0.0.1:8000/admin/`. Set up a superuser as shown above to manage the catalog and orders. Sample data can be safely re-seeded; existing sample products are updated by name.

## Application URLs

- `/` — home
- `/products/` — searchable catalog
- `/products/category/<slug>/` — category catalog
- `/products/<slug>/` — product detail
- `/accounts/register/`, `/accounts/login/`, `/accounts/profile/`
- `/cart/` — shopping cart
- `/orders/checkout/`, `/orders/history/`, `/orders/<id>/`
- `/admin/` — Django administration

## Cart and order behavior

The cart is stored in the visitor's Django session. Quantity changes and cart additions are checked against current stock. Checkout requires login, adds ₹99 delivery below ₹2,000 (free above that), and rechecks stock inside a database transaction before creating the order, preserving product names and prices on each order line and decrementing inventory. Orders and order details are only visible to their owner. Cash on Delivery completes directly. UPI and card selections enter a clearly labeled demo payment screen where the user can simulate success or cancel; no real payment is collected and card or UPI credentials are never requested. Product photos come from matching online product listings and are stored in `static/products/`, so the store serves the images locally.

## Database models

- `Category`: named product grouping and slug
- `Product`: searchable catalog item, price, optional discount, inventory, rating and image URL
- `Order`: customer and shipping details, order/payment statuses and total
- `OrderItem`: product snapshot, unit price and quantity for each order
- Django's built-in `User`: credentials and profile information

## Tests

Run the Django test suite with:

```bash
python manage.py test
```

Tests cover catalog/search, account flow, cart operations, stock validation and checkout/order totals.

## Future improvements

Integrate a payment gateway, add customer reviews, use image uploads, implement email notifications and add shipping tracking.
