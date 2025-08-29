#!/bin/bash
# clean_inactive_customers.sh

# Navigate to project root (adjust path if needed)
cd "$(dirname "$0")/../.." || exit

# Run Django shell and execute cleanup
python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)

inactive_customers = Customer.objects.exclude(
    orders__order_date__gte=one_year_ago
)

print(f"Found {inactive_customers.count()} inactive customers")

for customer in inactive_customers:
    print(f"Deleting {customer.name} ({customer.email})")
    customer.delete()
EOF

