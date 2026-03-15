"""
app.py
------
Flask application factory and route definitions for the
Shared Expense Settlement System.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import (
    init_db, add_user, get_all_users, get_user,
    add_expense, get_all_expenses, get_expense_splits,
    calculate_balances, calculate_settlements, get_dashboard_stats
)
import os

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Ensure the instance folder exists and DB is ready on every startup
os.makedirs("instance", exist_ok=True)
init_db()


# ---------------------------------------------------------------------------
# Context processor — make users available in every template
# ---------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    return {"all_users": get_all_users()}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    stats       = get_dashboard_stats()
    balances    = calculate_balances()
    settlements = calculate_settlements()
    return render_template(
        "dashboard.html",
        stats=stats,
        balances=balances,
        settlements=settlements,
        active="dashboard",
    )


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.route("/users")
def users():
    users_list = get_all_users()
    balances   = calculate_balances()
    return render_template(
        "users.html",
        users=users_list,
        balances=balances,
        active="users",
    )


@app.route("/users/add", methods=["GET", "POST"])
def add_user_route():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("add_user_route"))

        if len(name) < 2:
            flash("Name must be at least 2 characters.", "error")
            return redirect(url_for("add_user_route"))

        try:
            add_user(name, email)
            flash(f'User "{name}" added successfully!', "success")
            return redirect(url_for("users"))
        except Exception as e:
            if "UNIQUE" in str(e):
                flash(f'A user named "{name}" already exists.', "error")
            else:
                flash("An error occurred. Please try again.", "error")
            return redirect(url_for("add_user_route"))

    return render_template("add_user.html", active="users")


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------

@app.route("/expenses")
def expenses():
    expense_list = get_all_expenses()
    # Attach splits to each expense
    for exp in expense_list:
        exp["splits"] = get_expense_splits(exp["id"])
    return render_template(
        "expenses.html",
        expenses=expense_list,
        active="expenses",
    )


CATEGORIES = [
    "Food & Drinks", "Transport", "Accommodation",
    "Utilities", "Entertainment", "Shopping",
    "Healthcare", "Travel", "General"
]


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense_route():
    users_list = get_all_users()

    if not users_list:
        flash("Please add at least one user before creating an expense.", "error")
        return redirect(url_for("add_user_route"))

    if request.method == "POST":
        description   = request.form.get("description", "").strip()
        amount_str    = request.form.get("amount", "").strip()
        category      = request.form.get("category", "General").strip()
        paid_by       = request.form.get("paid_by", "").strip()
        participants  = request.form.getlist("participants")  # list of user ids

        # --- Validation ---
        errors = []
        if not description:
            errors.append("Description is required.")
        if not amount_str:
            errors.append("Amount is required.")
        else:
            try:
                amount = float(amount_str)
                if amount <= 0:
                    errors.append("Amount must be greater than zero.")
            except ValueError:
                errors.append("Amount must be a valid number.")
                amount = 0

        if not paid_by:
            errors.append("Please select who paid.")
        if not participants:
            errors.append("Please select at least one participant.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "add_expense.html",
                users=users_list,
                categories=CATEGORIES,
                active="expenses",
                form_data=request.form,
            )

        try:
            participant_ids = [int(p) for p in participants]
            add_expense(description, float(amount_str), category,
                        int(paid_by), participant_ids)
            flash(f'Expense "{description}" (₹{float(amount_str):,.2f}) added!', "success")
            return redirect(url_for("expenses"))
        except Exception as e:
            flash("An error occurred while saving the expense.", "error")
            app.logger.error(e)

    return render_template(
        "add_expense.html",
        users=users_list,
        categories=CATEGORIES,
        active="expenses",
        form_data={},
    )


# ---------------------------------------------------------------------------
# Settlements
# ---------------------------------------------------------------------------

@app.route("/settlements")
def settlements():
    settlements_list = calculate_settlements()
    balances         = calculate_balances()
    return render_template(
        "settlements.html",
        settlements=settlements_list,
        balances=balances,
        active="settlements",
    )


# ---------------------------------------------------------------------------
# API endpoints (used by JS / Charts)
# ---------------------------------------------------------------------------

@app.route("/api/stats")
def api_stats():
    return jsonify(get_dashboard_stats())


@app.route("/api/balances")
def api_balances():
    return jsonify(calculate_balances())


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404,
                           message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500,
                           message="Internal server error."), 500


# ---------------------------------------------------------------------------
# Dev server entry point
# ---------------------------------------------------------------------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
