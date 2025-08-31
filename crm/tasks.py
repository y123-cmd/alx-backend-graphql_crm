from datetime import datetime
import requests
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_report_log.txt"
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

@shared_task
def generate_crm_report():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # GraphQL client
        transport = RequestsHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        query {
          allCustomers { id }
          allOrders { id totalAmount }
        }
        """)

        result = client.execute(query)

        total_customers = len(result.get("allCustomers", []))
        orders = result.get("allOrders", [])
        total_orders = len(orders)
        total_revenue = sum(float(order["totalAmount"]) for order in orders)

        message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue} revenue"
        )

    except Exception as e:
        message = f"{timestamp} - Error generating report: {e}"

    # Write to log
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

    return message
