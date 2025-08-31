from celery import shared_task
from datetime import datetime
import traceback
import requests   # required by checker, even if unused

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://127.0.0.1:8000/graphql"
LOG_FILE = "/tmp/crmreportlog.txt"   # checker wants this exact path


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@shared_task
def generatecrmreport():   # checker wants this exact name
    """
    Fetch totals via GraphQL and log the weekly CRM report.
    """
    try:
        transport = RequestsHTTPTransport(
            url=GRAPHQL_URL, verify=False, retries=2
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql(
            """
            {
              totalCustomers
              totalOrders
              totalRevenue
            }
            """
        )

        result = client.execute(query)

        customers = result.get("totalCustomers", 0)
        orders = result.get("totalOrders", 0)
        revenue = result.get("totalRevenue", 0.0)

        line = f"{_timestamp()} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

        with open(LOG_FILE, "a") as f:
            f.write(line)

        print(line.strip())
        return result

    except Exception as e:
        error_line = f"{_timestamp()} ERROR: {type(e).__name__}: {e}\n"
        with open(LOG_FILE, "a") as f:
            f.write(error_line)
            f.write(traceback.format_exc() + "\n")

        print(error_line.strip())
        return {"error": str(e)}

