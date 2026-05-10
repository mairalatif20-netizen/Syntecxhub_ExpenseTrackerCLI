import csv
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("expense_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    category TEXT,
    amount REAL,
    date TEXT
)
""")

conn.commit()

# ---------- ADD TRANSACTION ----------
def add_transaction():
    t_type = input("Enter type (income/expense): ").lower()
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD): ")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format!")
        return

    cursor.execute("""
    INSERT INTO transactions (type, category, amount, date)
    VALUES (?, ?, ?, ?)
    """, (t_type, category, amount, date))

    conn.commit()
    print("Transaction added successfully!\n")

# ---------- VIEW TRANSACTIONS ----------
def view_transactions():
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()

    print("\n--- All Transactions ---")
    for row in rows:
        print(row)

# ---------- MONTHLY SUMMARY ----------
def monthly_summary():
    month = input("Enter month (YYYY-MM): ")

    cursor.execute("""
    SELECT type, SUM(amount)
    FROM transactions
    WHERE substr(date, 1, 7) = ?
    GROUP BY type
    """, (month,))

    rows = cursor.fetchall()

    income = 0
    expense = 0

    for row in rows:
        if row[0] == "income":
            income = row[1]
        elif row[0] == "expense":
            expense = row[1]

    balance = income - expense

    print(f"\n--- Summary for {month} ---")
    print("Total Income :", income)
    print("Total Expense:", expense)
    print("Balance      :", balance)

# ---------- EXPORT TO CSV ----------
def export_csv():
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()

    with open("transactions.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["ID", "Type", "Category", "Amount", "Date"])

        for row in rows:
            writer.writerow(row)

    print("Data exported to transactions.csv")

# ---------- EXPORT TO EXCEL ----------
def export_excel():
    query = "SELECT * FROM transactions"
    df = pd.read_sql_query(query, conn)

    df.to_excel("transactions.xlsx", index=False)

    print("Data exported to transactions.xlsx")

# ---------- GENERATE CHART ----------
def generate_chart():
    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE type='expense'
    GROUP BY category
    """)

    rows = cursor.fetchall()

    categories = []
    amounts = []

    for row in rows:
        categories.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(8, 5))
    plt.bar(categories, amounts)
    plt.xlabel("Category")
    plt.ylabel("Expense Amount")
    plt.title("Expenses by Category")

    plt.savefig("expense_chart.png")

    print("Chart saved as expense_chart.png")

# ---------- MAIN MENU ----------
while True:
    print("\n===== Expense Tracker CLI =====")
    print("1. Add Transaction")
    print("2. View Transactions")
    print("3. Monthly Summary")
    print("4. Export to CSV")
    print("5. Export to Excel")
    print("6. Generate Expense Chart")
    print("7. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        add_transaction()

    elif choice == "2":
        view_transactions()

    elif choice == "3":
        monthly_summary()

    elif choice == "4":
        export_csv()

    elif choice == "5":
        export_excel()

    elif choice == "6":
        generate_chart()

    elif choice == "7":
        print("Exiting...")
        break

    else:
        print("Invalid choice!")

conn.close()