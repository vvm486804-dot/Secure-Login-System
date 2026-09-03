# **🔐 Secure Login System**

A secure web-based authentication system built using **Python Flask, HTML, CSS, JavaScript, and SQLite**.

 ## **Features**
- User Registration
- Secure Login & Logout
- Bcrypt Password Hashing
- Input Validation
- SQL Injection Protection
- Session Management
- Optional Two-Factor Authentication (2FA)
- Responsive User Interface

## **Technologies Used**
- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- bcrypt
- PyOTP


## **Project Structure**
```text
secure-login-system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── enable_2fa.html
│   └── verify_2fa.html
│
└── static/
    ├── style.css
    └── script.js
```

## **How to Run**

1. Install dependencies
```text
pip install -r requirements.txt
```
2. Run the application
```text
python app.py
```
3. Open in browser
```text
http://127.0.0.1:5000
```
## **Security**
Passwords are securely stored using bcrypt hashing.
SQL queries use parameterized statements.
User input is validated on both client and server sides.
Flask sessions are used for authentication.
Optional TOTP-based 2FA provides additional security.

## **Requirements**
 User Registration
 User Login
 Hashed Passwords
 Input Validation
 SQL Injection Protection
 Session Management
 Logout
 Optional 2FA



