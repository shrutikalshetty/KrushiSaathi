from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

def get_db():
    return sqlite3.connect("krushisaathi.db")


def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # SAME OLD TABLES + user column (NO CHANGE IN STRUCTURE)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS crops(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        crop_name TEXT,
        season TEXT,
        income INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        expense_type TEXT,
        amount INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS soil(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        soil_type TEXT,
        ph_level TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()

# ---------------- AUTH ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "User already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- HOME ----------------
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    # ✅ Total Crops
    cur.execute("SELECT COUNT(*) FROM crops WHERE user=?", (session["user"],))
    total_crops = cur.fetchone()[0]

    # ✅ Total Income
    cur.execute("SELECT SUM(income) FROM crops WHERE user=?", (session["user"],))
    total_income = cur.fetchone()[0] or 0

    # ✅ Total Expenses
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user=?", (session["user"],))
    total_expense = cur.fetchone()[0] or 0

    # ✅ Profit
    profit = total_income - total_expense

    conn.close()

    return render_template(
        "home.html",
        crops=total_crops,
        income=total_income,
        expenses=total_expense,
        profit=profit,
        username=session["user"]
    )

# ---------------- CROPS ----------------

@app.route("/crops", methods=["GET", "POST"])
def crops():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO crops (user, crop_name, season, income) VALUES (?,?,?,?)",
            (session["user"], request.form["crop_name"], request.form["season"], request.form["income"])
        )
        conn.commit()

    cur.execute("SELECT * FROM crops WHERE user=?", (session["user"],))
    crops = cur.fetchall()

    conn.close()

    return render_template("crops.html", crops=crops, username=session["user"])


@app.route("/delete_crop/<int:id>")
def delete_crop(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM crops WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/crops")


# ---------------- EXPENSES ----------------

@app.route("/expenses", methods=["GET", "POST"])
def expenses():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO expenses (user, expense_type, amount) VALUES (?,?,?)",
            (session["user"], request.form["expense_type"], request.form["amount"])
        )
        conn.commit()

    cur.execute("SELECT * FROM expenses WHERE user=?", (session["user"],))
    expenses = cur.fetchall()

    conn.close()

    return render_template("expenses.html", expenses=expenses, username=session["user"])


@app.route("/delete_expense/<int:id>")
def delete_expense(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/expenses")

# ---------------- SOIL ----------------

@app.route("/soil", methods=["GET", "POST"])
def soil():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO soil (user, soil_type, ph_level, notes) VALUES (?,?,?,?)",
            (session["user"], request.form["soil_type"], request.form["ph_level"], request.form["notes"])
        )
        conn.commit()

    cur.execute("SELECT * FROM soil WHERE user=?", (session["user"],))
    soils = cur.fetchall()

    conn.close()

    return render_template("soil.html", soils=soils, username=session["user"])


# ✅ OUTSIDE FUNCTION (VERY IMPORTANT)
@app.route("/delete_soil/<int:id>")
def delete_soil(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM soil WHERE id=? AND user=?", (id, session["user"]))

    conn.commit()
    conn.close()

    return redirect("/soil")

# ---------------- PROFIT ----------------

@app.route("/profit")
def profit():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT SUM(income) FROM crops WHERE user=?", (session["user"],))
    income = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(amount) FROM expenses WHERE user=?", (session["user"],))
    expense = cur.fetchone()[0] or 0

    profit = income - expense

    conn.close()

    return render_template(
        "profit_loss.html",
        total_income=income,
        total_expense=expense,
        profit=profit,
        username=session["user"]
    )


# ---------------- GRAPH ----------------

@app.route("/graph")
def graph():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT expense_type, SUM(amount)
        FROM expenses
        WHERE user=?
        GROUP BY expense_type
    """, (session["user"],))

    data = cur.fetchall()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template("graph.html", labels=labels, values=values, username=session["user"])


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)