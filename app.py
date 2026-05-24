from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random, string, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

# ── MySQL config ──────────────────────────────────────────────────────────────
app.config["MYSQL_HOST"]     = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"]     = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"]       = os.environ.get("MYSQL_DB", "helpdesk")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# ── Auto-response templates ───────────────────────────────────────────────────
AUTO_RESPONSES = {
    "network":   "Your network issue has been received. Our team will diagnose connectivity within 2 hours.",
    "password":  "A password reset link has been sent to your registered email. Check your inbox.",
    "hardware":  "Your hardware request is logged. A technician will contact you to schedule a visit.",
    "software":  "We've noted your software issue. Please restart the application and update to the latest version.",
    "email":     "Email issues are typically resolved within 1 hour. We will notify you once the issue is fixed.",
    "default":   "Thank you for submitting your ticket. Our IT team will review it and respond within 4 business hours.",
}

def get_auto_response(title, description):
    combined = (title + " " + description).lower()
    for keyword, response in AUTO_RESPONSES.items():
        if keyword in combined:
            return response
    return AUTO_RESPONSES["default"]

def gen_ticket_id():
    return "TKT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ── Auth helpers ──────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form["name"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]
        role     = request.form.get("role", "user")   # hidden field; default user

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email already registered.", "danger")
            return render_template("register.html")

        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)",
            (name, email, hashed, role)
        )
        mysql.connection.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"]    = user["name"]
            session["role"]    = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("admin_panel") if user["role"] == "admin" else url_for("dashboard"))

        flash("Invalid credentials.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# ── User dashboard ────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM tickets WHERE user_id = %s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    tickets = cur.fetchall()

    stats = {
        "total":      len(tickets),
        "open":       sum(1 for t in tickets if t["status"] == "Open"),
        "in_progress":sum(1 for t in tickets if t["status"] == "In Progress"),
        "resolved":   sum(1 for t in tickets if t["status"] == "Resolved"),
    }
    return render_template("dashboard.html", tickets=tickets, stats=stats)


@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit_ticket():
    if request.method == "POST":
        title       = request.form["title"].strip()
        category    = request.form["category"]
        priority    = request.form["priority"]
        description = request.form["description"].strip()
        ticket_id   = gen_ticket_id()
        auto_reply  = get_auto_response(title, description)

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO tickets
               (ticket_id, user_id, title, category, priority, description, auto_response, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'Open')""",
            (ticket_id, session["user_id"], title, category, priority, description, auto_reply)
        )
        mysql.connection.commit()
        flash(f"Ticket {ticket_id} submitted! Auto-response: {auto_reply}", "success")
        return redirect(url_for("dashboard"))
    return render_template("submit.html")


@app.route("/ticket/<int:id>")
@login_required
def view_ticket(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tickets WHERE id = %s", (id,))
    ticket = cur.fetchone()

    if not ticket:
        flash("Ticket not found.", "danger")
        return redirect(url_for("dashboard"))

    if ticket["user_id"] != session["user_id"] and session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    cur.execute(
        """SELECT c.*, u.name FROM comments c
           JOIN users u ON c.user_id = u.id
           WHERE c.ticket_id = %s ORDER BY c.created_at""",
        (id,)
    )
    comments = cur.fetchall()

    cur.execute("SELECT id, name FROM users WHERE role = 'admin'")
    admins = cur.fetchall()
    return render_template("ticket.html", ticket=ticket, comments=comments, admins=admins)


@app.route("/ticket/<int:id>/comment", methods=["POST"])
@login_required
def add_comment(id):
    content = request.form["content"].strip()
    if content:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO comments (ticket_id, user_id, content) VALUES (%s,%s,%s)",
            (id, session["user_id"], content)
        )
        mysql.connection.commit()
    return redirect(url_for("view_ticket", id=id))

# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin_panel():
    status_filter   = request.args.get("status", "")
    priority_filter = request.args.get("priority", "")
    category_filter = request.args.get("category", "")

    query  = "SELECT t.*, u.name AS user_name, a.name AS admin_name FROM tickets t JOIN users u ON t.user_id=u.id LEFT JOIN users a ON t.assigned_to=a.id WHERE 1=1"
    params = []

    if status_filter:
        query += " AND t.status=%s"; params.append(status_filter)
    if priority_filter:
        query += " AND t.priority=%s"; params.append(priority_filter)
    if category_filter:
        query += " AND t.category=%s"; params.append(category_filter)

    query += " ORDER BY FIELD(t.priority,'Critical','High','Medium','Low'), t.created_at DESC"

    cur = mysql.connection.cursor()
    cur.execute(query, params)
    tickets = cur.fetchall()

    cur.execute("SELECT id, name FROM users WHERE role='admin'")
    admins = cur.fetchall()

    stats = {
        "total":       len(tickets),
        "open":        sum(1 for t in tickets if t["status"] == "Open"),
        "in_progress": sum(1 for t in tickets if t["status"] == "In Progress"),
        "resolved":    sum(1 for t in tickets if t["status"] == "Resolved"),
        "critical":    sum(1 for t in tickets if t["priority"] == "Critical"),
    }
    return render_template("admin.html", tickets=tickets, admins=admins,
                           stats=stats, filters={"status": status_filter,
                           "priority": priority_filter, "category": category_filter})


@app.route("/admin/ticket/<int:id>/update", methods=["POST"])
@admin_required
def update_ticket(id):
    status     = request.form.get("status")
    assigned   = request.form.get("assigned_to") or None
    resolution = request.form.get("resolution", "").strip()

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE tickets SET status=%s, assigned_to=%s, resolution=%s, updated_at=NOW() WHERE id=%s",
        (status, assigned, resolution, id)
    )
    mysql.connection.commit()
    flash("Ticket updated.", "success")
    return redirect(url_for("view_ticket", id=id))


@app.route("/admin/stats")
@admin_required
def stats_json():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT status, COUNT(*) as count FROM tickets GROUP BY status
    """)
    by_status = cur.fetchall()

    cur.execute("""
        SELECT category, COUNT(*) as count FROM tickets GROUP BY category
    """)
    by_category = cur.fetchall()

    return jsonify({"by_status": by_status, "by_category": by_category})


if __name__ == "__main__":
    app.run(debug=True)
