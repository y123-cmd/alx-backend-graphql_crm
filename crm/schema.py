# # import re
# import graphene
# from graphene_django import DjangoObjectType
# from django.core.exceptions import ValidationError
# from django.db import transaction

# from .models import Customer, Product, Order

# # ------------------ Types ------------------
# class CustomerType(DjangoObjectType):
#     class Meta:
#         model = Customer
#         fields = ("id", "name", "email", "phone")


# class ProductType(DjangoObjectType):
#     class Meta:
#         model = Product
#         fields = ("id", "name", "price", "stock")


# class OrderType(DjangoObjectType):
#     class Meta:
#         model = Order
#         fields = ("id", "customer", "products", "order_date", "total_amount")

# # ------------------ Mutations ------------------

# # 1. Create Customer
# class CreateCustomer(graphene.Mutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         email = graphene.String(required=True)
#         phone = graphene.String(required=False)

#     customer = graphene.Field(CustomerType)
#     message = graphene.String()

#     def mutate(self, info, name, email, phone=None):
#         if Customer.objects.filter(email=email).exists():
#             raise ValidationError("Email already exists")

#         if phone:
#             pattern = r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$'
#             if not re.match(pattern, phone):
#                 raise ValidationError("Invalid phone format")

#         customer = Customer.objects.create(name=name, email=email, phone=phone)
#         return CreateCustomer(customer=customer, message="Customer created successfully")


# # 2. Bulk Create Customers
# class BulkCreateCustomers(graphene.Mutation):
#     class Arguments:
#         customers = graphene.List(
#             graphene.NonNull(lambda: CreateCustomer.Arguments), required=True
#         )

#     customers = graphene.List(CustomerType)
#     errors = graphene.List(graphene.String)

#     @transaction.atomic
#     def mutate(self, info, customers):
#         created_customers = []
#         errors = []

#         for data in customers:
#             try:
#                 if Customer.objects.filter(email=data["email"]).exists():
#                     raise ValidationError(f"Email {data['email']} already exists")

#                 if "phone" in data and data["phone"]:
#                     pattern = r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$'
#                     if not re.match(pattern, data["phone"]):
#                         raise ValidationError(f"Invalid phone format: {data['phone']}")

#                 customer = Customer.objects.create(
#                     name=data["name"],
#                     email=data["email"],
#                     phone=data.get("phone")
#                 )
#                 created_customers.append(customer)

#             except ValidationError as e:
#                 errors.append(str(e))

#         return BulkCreateCustomers(customers=created_customers, errors=errors)


# # 3. Create Product
# class CreateProduct(graphene.Mutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         price = graphene.Float(required=True)
#         stock = graphene.Int(required=False, default_value=0)

#     product = graphene.Field(ProductType)

#     def mutate(self, info, name, price, stock=0):
#         if price <= 0:
#             raise ValidationError("Price must be positive")
#         if stock < 0:
#             raise ValidationError("Stock cannot be negative")

#         product = Product.objects.create(name=name, price=price, stock=stock)
#         return CreateProduct(product=product)


# # 4. Create Order
# class CreateOrder(graphene.Mutation):
#     class Arguments:
#         customer_id = graphene.ID(required=True)
#         product_ids = graphene.List(graphene.ID, required=True)
#         order_date = graphene.DateTime(required=False)

#     order = graphene.Field(OrderType)

#     def mutate(self, info, customer_id, product_ids, order_date=None):
#         try:
#             customer = Customer.objects.get(id=customer_id)
#         except Customer.DoesNotExist:
#             raise ValidationError("Invalid customer ID")

#         if not product_ids:
#             raise ValidationError("At least one product is required")

#         products = Product.objects.filter(id__in=product_ids)
#         if products.count() != len(product_ids):
#             raise ValidationError("Some product IDs are invalid")

#         order = Order.objects.create(customer=customer, order_date=order_date or None)
#         order.products.set(products)
#         order.calculate_total()

#         return CreateOrder(order=order)

# # ------------------ Schema Root ------------------
# class Query(graphene.ObjectType):
#     customers = graphene.List(CustomerType)
#     products = graphene.List(ProductType)
#     orders = graphene.List(OrderType)

#     def resolve_customers(root, info):
#         return Customer.objects.all()

#     def resolve_products(root, info):
#         return Product.objects.all()

#     def resolve_orders(root, info):
#         return Order.objects.all()


# class Mutation(graphene.ObjectType):
#     create_customer = CreateCustomer.Field()
#     bulk_create_customers = BulkCreateCustomers.Field()
#     create_product = CreateProduct.Field()
#     create_order = CreateOrder.Field()
import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "order_date", "customer", "products", "total_amount")


# ---------------- Queries ----------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)

    def resolve_customers(root, info, **kwargs):
        return Customer.objects.all()


# ---------------- Mutations ----------------
class CreateCustomer(graphene.Mutation):
    # ✅ Define arguments properly
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)

    customer = graphene.Field(CustomerType)

    @classmethod
    def mutate(cls, root, info, name, email):
        customer = Customer(name=name, email=email)
        customer.save()
        return CreateCustomer(customer=customer)


class UpdateCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        email = graphene.String(required=False)

    customer = graphene.Field(CustomerType)

    @classmethod
    def mutate(cls, root, info, id, name=None, email=None):
        try:
            customer = Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            raise Exception("Customer not found")

        if name is not None:
            customer.name = name
        if email is not None:
            customer.email = email
        customer.save()

        return UpdateCustomer(customer=customer)


class DeleteCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        try:
            customer = Customer.objects.get(pk=id)
            customer.delete()
            return DeleteCustomer(ok=True)
        except Customer.DoesNotExist:
            return DeleteCustomer(ok=False)


# Root Mutation
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    update_customer = UpdateCustomer.Field()
    delete_customer = DeleteCustomer.Field()
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info, **kwargs):
        return Customer.objects.all()

    def resolve_products(root, info, **kwargs):
        return Product.objects.all()

    def resolve_orders(root, info, **kwargs):
        return Order.objects.all()
schema = graphene.Schema(query=Query, mutation=Mutation)
