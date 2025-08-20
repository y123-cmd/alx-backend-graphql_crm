# Create a single customer
mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}

# Bulk create customers
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
  }
}

# Create a product
mutation {
  createProduct(input: {
    name: "Laptop",
    price: 999.99,
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
  }
}

# Create an order with products
mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
  }
}