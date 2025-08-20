import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")
django.setup()

from crm.models import Customer, Product

def seed():
    # Seed Customers
    Customer.objects.get_or_create(name="Alice", email="alice@example.com", phone="+1234567890")
    Customer.objects.get_or_create(name="Bob", email="bob@example.com", phone="123-456-7890")

    # Seed Products
    Product.objects.get_or_create(name="Laptop", price=999.99, stock=10)
    Product.objects.get_or_create(name="Phone", price=499.99, stock=25)

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
