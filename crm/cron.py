cat > crm/cron.py << 'PY'
#!/usr/bin/env python3
"""
Cron jobs for the CRM app.
log_crm_heartbeat will append a heartbeat line to /tmp/crm_heartbeat_log.txt
in the format: DD/MM/YYYY-HH:MM:SS CRM is alive
It will also attempt to query the GraphQL `hello` field and append status info.
"""

from datetime import datetime
import traceback

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
        import requests
        try:
            r = requests.post(GRAPHQL_URL, json={"query":"{ hello }"}, timeout=5)
            status = r.status_code
            if status == 200:
                j = r.json()
                if "data" in j and j["data"].get("hello") is not None:
                    extra = " (GraphQL hello OK)"
                elif "errors" in j:
                    extra = " (GraphQL returned errors)"
                else:
                    extra = " (GraphQL OK)"
            else:
                extra = f" (GraphQL status {status})"
        except Exception as e:
            extra = f" (GraphQL error: {type(e).__name__}: {e})"
    except Exception:
        extra = " (requests not available)"

    line = base + extra + "\n"
    try:
        with open(LOG_PATH, "a") as fh:
            fh.write(line)
    except Exception as e:
        # If writing fails, emit to stderr (cron will capture)
        print(f"Failed to write heartbeat: {e}")
        print(traceback.format_exc())

# For manual testing via `python crm/cron.py`
if __name__ == "__main__":
    log_crm_heartbeat()
    print("Heartbeat logged.")
PY

# make executable (not required but convenient)
chmod +x crm/cron.py
