# SplitWise Pro — Shared Expense Settlement System

> A portfolio-quality web application for managing shared expenses and calculating optimised debt settlements.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.10+ · Flask 3.x          |
| Database   | SQLite (via Python `sqlite3`)     |
| Frontend   | Jinja2 · HTML5 · CSS3 · Vanilla JS|
| Charts     | Chart.js 4.x (CDN)               |
| Fonts      | Syne · DM Sans (Google Fonts)     |

---

## Project Structure

```
expense-settlement/
│
├── app.py              # Flask routes & app factory
├── database.py         # SQLite helpers, schema, algorithm
├── seed.py             # Sample data loader
├── requirements.txt
│
├── instance/
│   └── expenses.db     # Auto-created SQLite database
│
├── templates/
│   ├── base.html       # Sidebar, topbar, flash messages
│   ├── dashboard.html  # Summary cards + charts
│   ├── users.html      # Member grid
│   ├── add_user.html   # Add member form
│   ├── expenses.html   # Searchable expense table
│   ├── add_expense.html# Expense form with participant picker
│   ├── settlements.html# Optimised settlement plan + balance chart
│   └── error.html      # 404 / 500 error page
│
└── static/
    ├── css/main.css    # Full design system (dark SaaS theme)
    └── js/main.js      # Sidebar toggle, Chart.js init
```

---

## Quick Start

### 1. Clone or Download

```bash
cd expense-settlement
```

### 2. Create a virtual environment

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Load sample data (optional but recommended)

```bash
python seed.py
```

This creates 4 users and 12 realistic expenses so you can explore the dashboard immediately.

### 5. Run the development server

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Features

### Dashboard
- Four summary cards: total expenses, active members, pending settlements, average per person
- Doughnut chart — spending by category
- Horizontal bar chart — amount paid per person
- Live net balance list
- Recommended settlement plan

### Users
- Add members with name + optional email
- Member card grid showing net balance status (owed / owes / settled)

### Expenses
- Log any expense: description, amount, category, payer, participants
- Equal split calculation with rounding correction
- Search + category filter on history table
- Participant avatar stack with tooltips

### Settlements
- Greedy min-transaction algorithm explanation banner
- Visual payment cards (A → ₹X → B)
- Per-person balance details
- Balance bar chart (green = owed, red = owes)

---

## Settlement Algorithm Explained

```
Input:  net balance for every user
        balance = total_paid − total_share_owed

Output: minimum list of (payer, receiver, amount) transactions

Steps:
  1. Separate users into creditors (balance > 0) and debtors (balance < 0).
  2. Sort both lists by absolute value, descending.
  3. Greedily pair the largest debtor with the largest creditor:
       transfer = min(|debtor_balance|, creditor_balance)
       Record the transfer.
       Reduce both balances by the transfer amount.
       Advance the pointer for whichever side reached zero.
  4. Repeat until all balances are within ε = 0.005 of zero.

This produces the minimum number of transactions needed.
```

### Example

| User   | Paid  | Share  | Net     |
|--------|-------|--------|---------|
| Alice  | ₹900  | ₹300   | **+₹600** |
| Bob    | ₹0    | ₹300   | **−₹300** |
| Carol  | ₹300  | ₹300   | **±₹0** |
| Dave   | ₹0    | ₹300   | **−₹300** |

Result: Bob → Alice ₹300, Dave → Alice ₹300. Just 2 transactions.

---

## Customisation Tips

- **Currency symbol**: Search `₹` in templates and replace with `$` / `€` etc.
- **Categories**: Edit the `CATEGORIES` list in `app.py`.
- **Colour scheme**: CSS variables are all in `:root {}` inside `main.css`.
- **Production deploy**: Use `gunicorn app:app` and set `SECRET_KEY` via environment variable.

---

## Screenshots

Run the app with seed data to see:
- Dark SaaS dashboard with live charts
- Responsive layout that works on mobile
- Real-time search and filter on the expense table
- Animated settlement cards with colour-coded avatars

---

*Built with Flask · SQLite · Chart.js*
