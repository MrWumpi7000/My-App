
from fastapi import FastAPI
import sqlite3
import hashlib

def add_email_to_online(email, online_list):
    online_list.append(email)
    print(f"Email {email} added to the online list.")

def delete_email_from_online(email, online_list):
    if email in online_list:
        online_list.remove(email)
        print(f"Email {email} deleted from the online list.")
    else:
        print(f"Email {email} not found in the online list.")

def list_online_emails(online_list):
    if online_list:
        print("Online emails:")
        for email in online_list:
            print(email)
    else:
        print("No emails are currently online.")

global online_emails
online_emails = []

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

@app.get("/OnlineUser/{email_id}")
def OnlineUser(email_id):
    print('Succes')
    add_email_to_online(email_id, online_emails)
    print(online_emails)
    return