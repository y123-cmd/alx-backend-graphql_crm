import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from crm.models import Product


# ---------------- Types ----------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email")


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
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info, **kwargs):
        return Customer.objects.all()

    def resolve_products(root, info, **kwargs):
        return Product.objects.all()

    def resolve_orders(root, info, **kwargs):
        return Order.objects.all()


# ---------------- Mutations ----------------
class CreateCustomer(graphene.Mutation):
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


# ---------------- New Mutation: UpdateLowStockProducts ----------------
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        increment = graphene.Int(required=False, default_value=10)

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, increment=10):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += increment
            product.save()
            updated.append(product)

        msg = f"Updated {len(updated)} products" if updated else "No products needed restocking"
        return UpdateLowStockProducts(updated_products=updated, message=msg)


# ---------------- Root Mutation ----------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    update_customer = UpdateCustomer.Field()
    delete_customer = DeleteCustomer.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


# ---------------- Schema ----------------
schema = graphene.Schema(query=Query, mutation=Mutation)

