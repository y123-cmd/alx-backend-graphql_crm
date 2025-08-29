#!/usr/bin/env python3
"""
Query local GraphQL endpoint for orders in the last 7 days and log reminders.
Logs to /tmp/order_reminders_log.txt and prints "Order reminders processed!".
"""

from datetime import datetime, timedelta, timezone
import sys

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

transport = RequestsHTTPTransport(
    url=GRAPHQL_URL,
    verify=False,
    retries=3,
    # If your GraphQL needs auth, add headers here like:
    # headers={"Authorization": "Bearer <TOKEN>"}
)
client = Client(transport=transport, fetch_schema_from_transport=False)

# Variants to try (adjust to match your schema if needed)
QUERY_VARIANTS = [
    """query { orders { id orderDate customer { email } } }""",
    """query { orders { id order_date customer { email } } }""",
    """query { allOrders { id orderDate customer { email } } }""",
    """query { allOrders { id order_date customer { email } } }""",
]

def try_fetch_orders():
    for q in QUERY_VARIANTS:
        try:
            result = client.execute(gql(q))
            orders = result.get("orders") or result.get("allOrders")
            if orders is not None:
                return orders
        except Exception:
            continue
    return None

def parse_iso_datetime(s):
    if not s:
        return None
    try:
        if isinstance(s, (int, float)):
            return datetime.fromtimestamp(s, tz=timezone.utc)
        if isinstance(s, str) and s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def main():
    orders = try_fetch_orders()
    if orders is None:
        print("ERROR: Could not fetch orders from GraphQL endpoint.", file=sys.stderr)
        sys.exit(1)

    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    lines_to_log = []

    for o in orders:
        oid = o.get("id") if isinstance(o, dict) else None
        cust = o.get("customer") if isinstance(o, dict) else {}
        email = cust.get("email") if isinstance(cust, dict) else None

        raw_date = o.get("orderDate") or o.get("order_date") or o.get("order_date")
        dt = parse_iso_datetime(raw_date) if raw_date else None

        if dt and dt >= one_week_ago:
            ts = datetime.now(timezone.utc).isoformat()
            line = f"{ts} - Order {oid} - {email}"
            lines_to_log.append(line)

    # append to log file
    if lines_to_log:
        with open(LOG_FILE, "a") as f:
            for ln in lines_to_log:
                f.write(ln + "\n")

    for ln in lines_to_log:
        print(ln)

    print("Order reminders processed!")

if __name__ == "__main__":
    main()
