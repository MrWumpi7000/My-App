
from fastapi import FastAPI
import sqlite3
import hashlib

def create_database():
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def register_user(email, password):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE email = ?
    ''', (email,))

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "User already exists. Please choose a different email."

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute('''
        INSERT INTO users (email, password)
        VALUES (?, ?)
    ''', (email, hashed_password))

    conn.commit()
    conn.close()

    return "Registration successful."

def login_user(email, password):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE email = ?
    ''', (email,))

    user = cursor.fetchone()

    conn.close()

    if user:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user[2] == hashed_password:
            return {
    "status": "User Logged in Successfully",
    "bool": True
} 
        else:
            return {
    "status": "Incorrect Password",
    "bool": False
}
    else:
        return {
    "status": "No User found",
    "bool": False
}

create_database()

login_result = login_user('example@email.com', 'securepassword123')
if login_result:
    print("Login successful.")
else:
    print("Login failed. Please check your email and password.")

app = FastAPI()

@app.get("/RegisterAnewAccount/{email_id},{password_id}")
def register_api(email_id, password_id):
    AccountStatus = register_user(email_id, password_id)
    jsonstring = {
    "status": AccountStatus,
    "bool": True
}

    return jsonstring


@app.get("/LoginIntoAaccount/{email_id},{password_id}")
def login_api(email_id, password_id):
    AccountStatus = login_user(email_id, password_id)
    return AccountStatus