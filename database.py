"""
database.py
-----------
Handles all SQLite database operations: initialization, schema creation,
and CRUD helpers for users, expenses, and settlements.
"""

import sqlite3
from datetime import datetime

DATABASE_PATH = "instance/expenses.db"

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_db():
    """Return a new SQLite connection with row_factory set to Row."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Schema initialization
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL UNIQUE,
    email     TEXT,
    avatar    TEXT,                      -- initials or emoji
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT    NOT NULL,
    amount      REAL    NOT NULL CHECK(amount > 0),
    category    TEXT    NOT NULL DEFAULT 'General',
    paid_by     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS expense_splits (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id  INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    share       REAL    NOT NULL    -- absolute amount this user owes
);
"""


def init_db():
    """Create tables if they don't already exist."""
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def add_user(name: str, email: str = "") -> int:
    """Insert a new user; returns the new row id."""
    initials = "".join(p[0].upper() for p in name.strip().split()[:2])
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO users (name, email, avatar) VALUES (?, ?, ?)",
        (name.strip(), email.strip(), initials),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_all_users():
    """Return all users ordered by name."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Expense helpers
# ---------------------------------------------------------------------------

def add_expense(description: str, amount: float, category: str,
                paid_by: int, participant_ids: list) -> int:
    """
    Insert an expense and create equal splits among participants.
    Returns the new expense id.
    """
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO expenses (description, amount, category, paid_by) VALUES (?, ?, ?, ?)",
        (description.strip(), round(float(amount), 2), category.strip(), paid_by),
    )
    expense_id = cur.lastrowid

    # Equal split among all participants
    share = round(float(amount) / len(participant_ids), 2)
    # Fix rounding: assign remainder to first participant
    remainder = round(float(amount) - share * len(participant_ids), 2)

    for i, uid in enumerate(participant_ids):
        s = share + (remainder if i == 0 else 0)
        conn.execute(
            "INSERT INTO expense_splits (expense_id, user_id, share) VALUES (?, ?, ?)",
            (expense_id, uid, round(s, 2)),
        )

    conn.commit()
    conn.close()
    return expense_id


def get_all_expenses():
    """Return all expenses with payer name, ordered newest first."""
    conn = get_db()
    rows = conn.execute("""
        SELECT e.*, u.name AS payer_name
        FROM   expenses e
        JOIN   users    u ON u.id = e.paid_by
        ORDER  BY e.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_expense_splits(expense_id: int):
    """Return per-user splits for a given expense."""
    conn = get_db()
    rows = conn.execute("""
        SELECT es.*, u.name AS user_name
        FROM   expense_splits es
        JOIN   users          u  ON u.id = es.user_id
        WHERE  es.expense_id = ?
    """, (expense_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Settlement / balance calculation
# ---------------------------------------------------------------------------

def calculate_balances():
    """
    Return a dict: {user_id: net_balance}

    Positive  → this user is owed money (paid more than their share).
    Negative  → this user owes money    (paid less than their share).

    Algorithm
    ---------
    For every expense:
        payer_credit[paid_by]  += total_amount
        each split contributor owes their share  → debit[user_id] += share

    net = credit - debit
    """
    conn = get_db()

    users = {u["id"]: u["name"] for u in get_all_users()}
    balances = {uid: 0.0 for uid in users}

    expenses = conn.execute("SELECT id, amount, paid_by FROM expenses").fetchall()
    for exp in expenses:
        balances[exp["paid_by"]] = round(balances[exp["paid_by"]] + exp["amount"], 2)

    splits = conn.execute("SELECT user_id, share FROM expense_splits").fetchall()
    for s in splits:
        balances[s["user_id"]] = round(balances[s["user_id"]] - s["share"], 2)

    conn.close()

    return {uid: {"name": users[uid], "balance": round(bal, 2)}
            for uid, bal in balances.items()}


def calculate_settlements():
    """
    Simplify debts using the greedy min-transaction algorithm.

    Returns a list of dicts:
        {from_id, from_name, to_id, to_name, amount}

    Steps
    -----
    1. Compute net balance for every user.
    2. Separate into creditors (balance > 0) and debtors (balance < 0).
    3. Greedily match the largest debtor with the largest creditor until
       all balances reach zero (within a ε tolerance).
    """
    raw = calculate_balances()

    creditors = []   # (amount, user_id, name)
    debtors   = []   # (amount, user_id, name)  — amount is positive here

    for uid, info in raw.items():
        b = info["balance"]
        if b > 0.005:
            creditors.append([b, uid, info["name"]])
        elif b < -0.005:
            debtors.append([-b, uid, info["name"]])

    creditors.sort(reverse=True)
    debtors.sort(reverse=True)

    settlements = []

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debt   = debtors[i][0]
        credit = creditors[j][0]
        amount = round(min(debt, credit), 2)

        settlements.append({
            "from_id":   debtors[i][1],
            "from_name": debtors[i][2],
            "to_id":     creditors[j][1],
            "to_name":   creditors[j][2],
            "amount":    amount,
        })

        debtors[i][0]   = round(debt   - amount, 2)
        creditors[j][0] = round(credit - amount, 2)

        if debtors[i][0]   < 0.005: i += 1
        if creditors[j][0] < 0.005: j += 1

    return settlements


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------

def get_dashboard_stats():
    """Return summary numbers for the dashboard cards."""
    conn = get_db()

    total = conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]
    expense_count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    user_count    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # Per-category totals for chart
    cat_rows = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM   expenses
        GROUP  BY category
        ORDER  BY total DESC
    """).fetchall()

    # Per-user paid totals
    user_rows = conn.execute("""
        SELECT u.name, COALESCE(SUM(e.amount),0) AS total
        FROM   users    u
        LEFT JOIN expenses e ON e.paid_by = u.id
        GROUP  BY u.id
        ORDER  BY total DESC
    """).fetchall()

    conn.close()

    return {
        "total_expenses":  round(total, 2),
        "expense_count":   expense_count,
        "user_count":      user_count,
        "by_category":     [dict(r) for r in cat_rows],
        "by_user":         [dict(r) for r in user_rows],
    }
