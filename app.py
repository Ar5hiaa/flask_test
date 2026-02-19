from flask import Flask, render_template, request, redirect, session
import database

app = Flask(__name__)
app.secret_key = "mysecretkey"

database.init_db()


@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")
    
    conn = database.connect()
    cursor = conn.cursor()

    search_query = request.args.get("search")

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]

        cursor.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            (name, age)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    if search_query:
        users = cursor.execute(
            "SELECT * FROM users WHERE name LIKE ?",
            ('%' + search_query + '%',)
        ).fetchall()
    else:
        users = cursor.execute("SELECT * FROM users").fetchall()

    conn.close()
    return render_template("index.html", users=users)


@app.route("/delete/<int:user_id>")
def delete(user_id):
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit(user_id):
    conn = database.connect()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]

        cursor.execute(
            "UPDATE users SET name = ?, age = ? WHERE id = ?",
            (name, age, user_id)
        )

        conn.commit()
        conn.close()
        return redirect("/")

    user = cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")
    print("ACCOUNTS TABLE:", cursor.fetchall())

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = cursor.execute(
            "SELECT * FROM accounts WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "نام کاربری یا رمز اشتباه است"

    return render_template("login.html")


@app.route("/create_admin")
def create_admin():
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO accounts (username, password) VALUES (?, ?)",
        ("admin", "1234")
    )

    conn.commit()
    conn.close()

    return "Admin created!"


if __name__ == "__main__":
    app.run(debug=True)