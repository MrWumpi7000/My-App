
from fastapi import FastAPI
import sqlite3
import hashlib
import uvicorn

global online_emails
online_emails = []

def add_email_to_online(email, online_list):
    if email in online_list:
        print('Email is already in list')
    else:
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

def AddUserIDtoEmail(email, email_friend):
    conn = sqlite3.connect('My-App/My-App/user_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE email=?', (email,))
    user_id = cursor.fetchone()
    cursor.execute('SELECT id FROM users WHERE email=?', (email_friend,))
    friend_id = cursor.fetchone()


    if user_id and friend_id:
        cursor.execute('''
            INSERT INTO friendships (user_id, friend_id)
            SELECT ?, ? WHERE NOT EXISTS (
                SELECT 1 FROM friendships
                WHERE (
                    user_id = ?
                    AND friend_id = ?
                )
            )
        ''', (
            str(user_id[0]),
            str(friend_id[0]),
            str(user_id[0]),
            str(friend_id[0])
        ))

        conn.commit()

        if cursor.rowcount > 0:
            print("Friendship added successfully.")
        else:
            print("Friendship already exists.")

    elif user_id is None:
        print(f"User with email '{email}' not found.")
    elif friend_id is None:
        print(f"Friend with email '{email_friend}' not found.")

    conn.close()

def get_chat_messages(user_id:str, friend_id:str):
    conn = sqlite3.connect('My-App/My-App/user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (user_id,))
    
    user_id = cursor.fetchone()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (friend_id,))

    friend_id = cursor.fetchone()

    cursor.execute('''
        SELECT message FROM chatmessages
        WHERE (user_id = ?
            AND friend_id = ?)
                OR (friend_id = ?
                   AND user_id = ?)
        ORDER BY timestamp ASC
    ''', (str(user_id[0]), str(friend_id[0]), str(user_id[0]), str(friend_id[0])))

    messages = cursor.fetchall()

    for message in messages:
        print(message)

    return messages
def save_chat_messages(user_id:str, friend_id:str, chat_message:str):
    conn = sqlite3.connect('My-App/My-App/user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (user_id,))
    
    user_id = cursor.fetchone()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (friend_id,))

    friend_id = cursor.fetchone()

    cursor.execute('''
        INSERT INTO chatmessages (user_id, friend_id, message)
        VALUES (?, ?, ?)
    ''', (str(user_id[0]), str(friend_id[0]), str(chat_message)))
    
    conn.commit()
    conn.close()

def get_friend_list(email):
    conn = sqlite3.connect('My-App/My-App/user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (email,))

    user_id = cursor.fetchone()

    if user_id:
        print(user_id[0])
        cursor.execute('''
            SELECT
                usr.email AS user_email,
                frnds.email AS friend_email
            FROM friendships
            LEFT JOIN users frnds ON friendships.friend_id = frnds.id
            LEFT JOIN users usr ON usr.id = friendships.user_id
            WHERE friendships.user_id = ?
        ''', (str(user_id[0])))

        friend_list = [row[1] for row in cursor.fetchall()]
        print(f"Friend list for '{email}': {friend_list}")
        return friend_list
    else:
        print(f"User with email '{email}' not found.")

    conn.close()

def create_database():
    conn = sqlite3.connect('My-App/My-App/user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT NOT NULL,
            friend_id INT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chatmessages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT NOT NULL,
            friend_id INT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
    ''')

    conn.commit()
    conn.close()

def register_user(email, password):
    conn = sqlite3.connect('My-App/My-App/user_database.db')
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
    conn = sqlite3.connect('My-App/My-App/user_database.db')
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

app = FastAPI()

@app.post("/RegisterAnewAccount/{email_id},{password_id}")
def register_api(email_id, password_id):
    AccountStatus = register_user(email_id, password_id)
    jsonstring = {
    "status": AccountStatus,
    "bool": True
}

    return jsonstring


@app.post("/LoginIntoAaccount/{email_id},{password_id}")
def login_api(email_id, password_id):
    AccountStatus = login_user(email_id, password_id)
    return AccountStatus

@app.post("/OnlineUser/{email_id}")
def OnlineUser(email_id):
    add_email_to_online(email_id, online_emails)
    print(online_emails)
    return

@app.get("/ListOnlineUsers")
def ListOnlineUsers():
    list_online_emails(online_emails)
    jsonstring = {
    "onlineusers": online_emails
}
    return jsonstring

@app.post("/AddToFriendList/{email_id},{friend_email_id}")
def AddToFriendList(email_id, friend_email_id):
    AddUserIDtoEmail(email=email_id, email_friend=friend_email_id)
    return

@app.post("/PostMessages/{user_id},{friend_id},{message}")
def PostMessages(user_id, friend_id, message):
    save_chat_messages(user_id=user_id, friend_id=friend_id, chat_message=message)
    return True

@app.get("/GetAllMessages/{user_id},{friend_id}")
def GetAllMessages(user_id, friend_id):
    messages = get_chat_messages(user_id=user_id, friend_id=friend_id)
    return messages

@app.get("/GetAllFriends/{email_id}")
def AddToFriendList(email_id):
    friends = get_friend_list(email=email_id)
    jsonstring = {
        "friends": friends
    }
    return jsonstring

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)