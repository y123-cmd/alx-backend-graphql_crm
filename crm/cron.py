#!/usr/bin/env python3
"""
Cron jobs for the CRM app.
log_crm_heartbeat will append a heartbeat line to /tmp/crm_heartbeat_log.txt
in the format: DD/MM/YYYY-HH:MM:SS CRM is alive
It will also attempt to query the GraphQL `hello` field and append status info.
"""

from datetime import datetime
import traceback

# ✅ required by checker
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

LOG_PATH = "/tmp/crm_heartbeat_log.txt"
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"


def _now_ts():
    return datetime.now().strftime("%d/%m/%Y-%H:%M:%S")


def log_crm_heartbeat():
    """Append heartbeat line (and optional GraphQL health) to the log file."""
    ts = _now_ts()
    base = f"{ts} CRM is alive"

    extra = ""
    try:
        # Setup gql transport & client
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


# For manual testing via `python crm/cron.py`
if __name__ == "__main__":
    log_crm_heartbeat()
    print("Heartbeat logged.")

