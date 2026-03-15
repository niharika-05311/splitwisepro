"""
seed.py
-------
Populates the database with realistic sample data for testing and demos.
Run once after setting up the project:  python seed.py
"""

import os
os.makedirs("instance", exist_ok=True)

from database import init_db, add_user, add_expense, get_all_users

init_db()

# Check if already seeded
users = get_all_users()
if users:
    print("Database already has data — skipping seed.")
    exit()

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
print("Seeding users...")
user_names = ["Arjun Mehta", "Priya Sharma", "Rohan Das", "Sneha Patel"]
for name in user_names:
    add_user(name)

users = get_all_users()
ids   = {u["name"]: u["id"] for u in users}

# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
print("Seeding expenses...")
all_ids = list(ids.values())

expenses = [
    ("Goa Trip Hotel",         12800, "Accommodation", ids["Arjun Mehta"],  all_ids),
    ("Flight Tickets",         18400, "Travel",         ids["Priya Sharma"], all_ids),
    ("Dinner at Toit",          2400, "Food & Drinks",  ids["Rohan Das"],    all_ids),
    ("Cab to Airport",           960, "Transport",      ids["Sneha Patel"],  all_ids),
    ("Groceries for the week",  1850, "Shopping",       ids["Arjun Mehta"],  all_ids),
    ("Netflix Subscription",     649, "Entertainment",  ids["Priya Sharma"], all_ids),
    ("Electricity Bill",        2200, "Utilities",      ids["Rohan Das"],    all_ids),
    ("Pizza Night",             1350, "Food & Drinks",  ids["Sneha Patel"],  all_ids),
    ("Museum Tickets",           800, "Entertainment",  ids["Arjun Mehta"],  all_ids),
    ("Water Bill",               450, "Utilities",      ids["Priya Sharma"], all_ids),
    ("Breakfast Buffet",        1100, "Food & Drinks",  ids["Rohan Das"],    all_ids),
    ("Taxi — City Tour",         720, "Transport",      ids["Sneha Patel"],  all_ids),
]

for desc, amt, cat, paid_by, parts in expenses:
    add_expense(desc, amt, cat, paid_by, parts)

print(f"✅  Seeded {len(users)} users and {len(expenses)} expenses.")
print("    Run:  python app.py   — then open http://127.0.0.1:5000")
