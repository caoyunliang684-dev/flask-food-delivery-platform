# Enjoy! Food Delivery Platform

A food delivery web application built with Flask and PostgreSQL. Customers order from restaurants, restaurants manage their menus and incoming orders, and couriers pick up and deliver orders.

University database course project. Page text is in French and Chinese; route and table names are in French.

## Features

**Customers**
- Register and log in (passwords are stored as hashes)
- Search restaurants by name, rating, number of reviews or keyword
- Order dishes, view order history and cancel an order
- Rate a restaurant after an order
- Loyalty points and referral of other customers

**Restaurants**
- Log in, view incoming orders
- Edit restaurant details and the dishes and prices on offer

**Couriers**
- Log in, choose the city they work in
- Pick an order, then mark it as delivered

## Tech stack

- Python, Flask, Jinja2 templates, HTML/CSS
- PostgreSQL through Psycopg2
- 34 routes in `main.py`, 26 templates, and a 12-table schema (`projet`) covering customers, restaurants, couriers, dishes, offers, orders, deliveries, ratings and cities

## Setup

Requires Python 3 and PostgreSQL.

```sh
pip install flask psycopg2-binary

# Load the schema and sample data
psql -U postgres -d postgres -f enjoy.dmp

# Database connection (standard PostgreSQL variables)
export PGPASSWORD=your_password
# optional: PGHOST, PGPORT, PGDATABASE, PGUSER (default: localhost, 5432, postgres, postgres)
# optional: FLASK_SECRET_KEY to keep sessions across restarts

python main.py
```

Then open http://127.0.0.1:5000/accueil.

## Files

| Path | Purpose |
| --- | --- |
| `main.py` | Flask routes and application logic |
| `db.py` | Database connection |
| `enjoy.dmp` | PostgreSQL dump: schema and sample data |
| `templates/` | Jinja2 pages for customers, restaurants and couriers |
| `static/style.css` | Styles |
