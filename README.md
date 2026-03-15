# SplitWisePro – Collaborative Expense Management System

SplitWisePro is a full-stack web application that helps groups manage shared expenses and automatically calculate settlements.

The system allows users to add members, record expenses, and determine who owes whom using an optimized settlement algorithm.

---

## Features

• Add and manage group members  
• Record shared expenses  
• View expense history  
• Automatic expense splitting  
• Settlement calculation between users  
• Dashboard with charts and analytics  

---

## Tech Stack

### Backend
Python, Flask

### Frontend
HTML, CSS, JavaScript, Chart.js

### Database
SQLite

---

## Settlement Algorithm

The application uses a **Greedy Minimum Transactions Algorithm** to minimize the number of payments required to settle debts between users.

### Steps

1. Calculate each user's net balance  
2. Separate creditors and debtors  
3. Match the largest debtor with the largest creditor  
4. Continue until all balances are settled  

This approach reduces unnecessary transactions and efficiently settles group expenses.

---

## Running the Project

### Clone the repository

```
git clone https://github.com/YOURUSERNAME/splitwisepro
```

### Navigate to the project folder

```
cd splitwisepro
```

### Install dependencies

```
pip install -r requirements.txt
```

### Run the application

```
python app.py
```

### Open in browser

```
http://127.0.0.1:5000
```

---

## Live Demo

https://splitwisepro.onrender.com

---

## Project Structure

```
splitwisepro
│
├ app.py
├ database.py
├ seed.py
├ requirements.txt
├ README.md
│
├ static
│   ├ css
│   │   └ main.css
│   └ js
│       └ main.js
│
└ templates
    ├ base.html
    ├ dashboard.html
    ├ users.html
    ├ expenses.html
    ├ settlements.html
    ├ add_user.html
    ├ add_expense.html
    └ error.html
```

---

## Author

Developed a project for learning full-stack web development using Flask.
