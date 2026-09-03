🔐 Secure Login System

A secure web-based authentication system built using Python Flask, HTML, CSS, JavaScript, and SQLite.

*Features*

User Registration

Secure Login & Logout

Bcrypt Password Hashing

Input Validation

SQL Injection Protection

Session Management

Optional Two-Factor Authentication (2FA)

Responsive User Interface

*Technologies*

Python & Flask

SQLite

HTML5 & CSS3

JavaScript

bcrypt

PyOTP



*Project Structure*

secure_login_system/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── enable_2fa.html
│   └── verify_2fa.html
└── static/
    ├── style.css
    └── script.js

*How to Run*

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open in your browser:

http://127.0.0.1:5000

*Security*

Passwords are stored using bcrypt hashing.

SQL queries use parameterized statements.

User input is validated on the client and server.

Flask sessions protect authenticated pages.

Optional TOTP-based 2FA provides an additional security layer.

*Requirements*

User Registration

User Login

Hashed Passwords

Input Validation

SQL Injection Protection

Session Management

Logout

Optional 2FA


📄 License

For educational and academic purposes.
