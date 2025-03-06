import sqlite3
from datetime import datetime, timedelta

def get_notifications(uid):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    notifications = []

    #Check if spending exceeded budget
    c.execute('''
        SELECT c.name, b.amount, 
               (SELECT COALESCE(SUM(t.amount), 0) 
                FROM transactions t 
                WHERE t.cid = b.cid AND t.uid = ? 
                AND DATE(t.date) BETWEEN DATE(b.start_date) AND DATE(b.end_date)) AS total_spent
        FROM budget b
        JOIN categories c ON b.cid = c.cid
        WHERE b.uid = ?;
    ''', (uid, uid))

    for row in c.fetchall():
        category_name, budget_amount, total_spent = row
        if total_spent is None:  # Extra safety check
            total_spent = 0

        if total_spent > budget_amount:
            notifications.append(f"⚠️ Budget exceeded for '{category_name}'! (Spent: ₹{total_spent}, Budget: ₹{budget_amount})")

    # Check if a budget is ending soon (within 3 days)
    today = datetime.now().date()
    upcoming_date = today + timedelta(days=3)
    c.execute('''
        SELECT c.name FROM budget b
        JOIN categories c ON b.cid = c.cid
        WHERE b.uid = ? AND DATE(b.end_date) BETWEEN DATE(?) AND DATE(?);
    ''', (uid, today, upcoming_date))  # Check budgets expiring in the next 3 days

    for row in c.fetchall():
        category_name = row[0]
        notifications.append(f"⏳ Budget for '{category_name}' expires soon!")

    conn.close()
    return notifications
