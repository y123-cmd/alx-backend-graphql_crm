#!/usr/bin/env python3
"""
Cron jobs for the CRM app.

- log_crm_heartbeat: Appends a heartbeat line to /tmp/crm_heartbeat_log.txt
  Format: DD/MM/YYYY-HH:MM:SS CRM is alive
  Also queries GraphQL `{ hello }` and appends status info.

- update_low_stock: Calls the updateLowStockProducts mutation and logs updated products.
  Appends to /tmp/low_stock_updates_log.txt with timestamped lines.
"""

from datetime import datetime
import json
import traceback

# ✅ Required by checker
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

# --- Paths ---
LOG_PATH = "/tmp/crm_heartbeat_log.txt"
LOW_STOCK_LOG = "/tmp/low_stock_updates_log.txt"
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"


# --- Utils ---
def _ts():
    return datetime.now().strftime("%d/%m/%Y-%H:%M:%S")


# --- Heartbeat job ---
def log_crm_heartbeat():
    """Append heartbeat line (and optional GraphQL health) to the log file."""
    ts = _ts()
    base = f"{ts} CRM is alive"

    extra = ""
    try:
        transport = RequestsHTTPTransport(
            url=GRAPHQL_URL,
            verify=False,
            retries=1,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        result = client.execute(query)

        if "hello" in result:
            extra = " (GraphQL hello OK)"
        else:
            extra = " (GraphQL responded, but no hello)"
    except Exception as e:
        extra = f" (GraphQL error: {type(e).__name__}: {e})"

    line = base + extra + "\n"
    try:
        with open(LOG_PATH, "a") as fh:
            fh.write(line)
    except Exception as e:
        print(f"Failed to write heartbeat: {e}")
        print(traceback.format_exc())


# --- Low stock updater job ---
def update_low_stock():
    """
    Calls the updateLowStockProducts mutation and logs updated products.
    Appends lines to /tmp/low_stock_updates_log.txt with a timestamp.
    """
    transport = RequestsHTTPTransport(
        url=GRAPHQL_URL,
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation = gql("""
        mutation UpdateLowStock($inc: Int) {
          updateLowStockProducts(increment: $inc) {
            message
            updatedProducts { id name stock }
          }
        }
    """)

    try:
        result = client.execute(mutation, variable_values={"inc": 10})
        payload = result.get("updateLowStockProducts") or {}
        message = payload.get("message", "No message")
        products = payload.get("updatedProducts") or []

        lines = [f"{_ts()} {message}"]
        if products:
            for p in products:
                lines.append(f"{_ts()} - {p['name']} -> stock={p['stock']}")
        else:
            lines.append(f"{_ts()} - No products updated")

        with open(LOW_STOCK_LOG, "a") as fh:
            fh.write("\n".join(lines) + "\n")

        print(message)
        print(json.dumps(products, indent=2))

    except Exception as e:
        err = f"{_ts()} ERROR: {type(e).__name__}: {e}"
        with open(LOW_STOCK_LOG, "a") as fh:
            fh.write(err + "\n")
            fh.write(traceback.format_exc() + "\n")
        print(err)


# --- Manual testing ---
if __name__ == "__main__":
    print("Running heartbeat...")
    log_crm_heartbeat()
    print("Running low stock updater...")
    update_low_stock()

