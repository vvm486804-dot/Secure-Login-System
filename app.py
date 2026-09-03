from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import bcrypt
import pyotp
import qrcode
import io
import base64
import re
import os
from functools import wraps

app = Flask(__name__)

# Change this to a long random value for a real deployment.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-for-production"
)

DATABASE = "users.db"

# Session security settings
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = 1800


# -------------------------------------------------
# DATABASE
# -------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            two_fa_enabled INTEGER DEFAULT 0,
            two_fa_secret TEXT
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# VALIDATION
# -------------------------------------------------

def valid_username(username):
    return re.fullmatch(r"[A-Za-z0-9_]{3,30}", username) is not None


def valid_email(email):
    return re.fullmatch(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email
    ) is not None


def valid_password(password):
    return (
        len(password) >= 8
        and re.search(r"[A-Za-z]", password)
        and re.search(r"\d", password)
    )


# -------------------------------------------------
# LOGIN REQUIRED
# -------------------------------------------------

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# -------------------------------------------------
# REGISTER
# -------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation
        if not valid_username(username):
            flash(
                "Username must contain 3-30 letters, numbers or underscores.",
                "error"
            )
            return render_template("register.html")

        if not valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if not valid_password(password):
            flash(
                "Password must be at least 8 characters and contain letters and numbers.",
                "error"
            )
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        # Hash password with bcrypt
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        conn = get_db()

        try:

            # Parameterized SQL query protects against SQL injection
            conn.execute(
                """
                INSERT INTO users
                (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    password_hash.decode("utf-8")
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            flash(
                "Username or email already exists.",
                "error"
            )

            conn.close()

            return render_template("register.html")

        conn.close()

        flash(
            "Registration successful. You can now login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        # Parameterized query
        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if user:

            password_correct = bcrypt.checkpw(
                password.encode("utf-8"),
                user["password_hash"].encode("utf-8")
            )

            if password_correct:

                # If 2FA is enabled
                if user["two_fa_enabled"] == 1:

                    session.clear()

                    session["pending_2fa_user"] = user["id"]

                    return redirect(
                        url_for("verify_2fa")
                    )

                # Normal login
                session.clear()

                session.permanent = True

                session["user_id"] = user["id"]
                session["username"] = user["username"]

                flash(
                    "Login successful.",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template("login.html")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        user=user
    )


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# -------------------------------------------------
# ENABLE 2FA
# -------------------------------------------------

@app.route("/enable-2fa", methods=["GET", "POST"])
@login_required
def enable_2fa():

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if request.method == "POST":

        otp = request.form.get("otp", "").strip()

        if user["two_fa_secret"] is None:

            secret = pyotp.random_base32()

            conn.execute(
                """
                UPDATE users
                SET two_fa_secret = ?
                WHERE id = ?
                """,
                (
                    secret,
                    user["id"]
                )
            )

            conn.commit()

        else:

            secret = user["two_fa_secret"]

        totp = pyotp.TOTP(secret)

        if totp.verify(otp):

            conn.execute(
                """
                UPDATE users
                SET two_fa_enabled = 1
                WHERE id = ?
                """,
                (user["id"],)
            )

            conn.commit()
            conn.close()

            flash(
                "Two-Factor Authentication enabled successfully.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid authentication code.",
            "error"
        )

    else:

        if user["two_fa_secret"] is None:

            secret = pyotp.random_base32()

            conn.execute(
                """
                UPDATE users
                SET two_fa_secret = ?
                WHERE id = ?
                """,
                (
                    secret,
                    user["id"]
                )
            )

            conn.commit()

        else:

            secret = user["two_fa_secret"]

    # Create QR code
    totp = pyotp.TOTP(secret)

    uri = totp.provisioning_uri(
        name=user["email"],
        issuer_name="Secure Login System"
    )

    qr = qrcode.make(uri)

    buffer = io.BytesIO()

    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode()

    conn.close()

    return render_template(
        "enable_2fa.html",
        secret=secret,
        qr_code=qr_base64
    )


# -------------------------------------------------
# VERIFY 2FA DURING LOGIN
# -------------------------------------------------

@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():

    if "pending_2fa_user" not in session:
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        otp = request.form.get("otp", "").strip()

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (session["pending_2fa_user"],)
        ).fetchone()

        if user:

            totp = pyotp.TOTP(
                user["two_fa_secret"]
            )

            if totp.verify(otp):

                session.clear()

                session.permanent = True

                session["user_id"] = user["id"]
                session["username"] = user["username"]

                conn.close()

                flash(
                    "Two-Factor Authentication successful.",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

        conn.close()

        flash(
            "Invalid authentication code.",
            "error"
        )

    return render_template(
        "verify_2fa.html"
    )


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )