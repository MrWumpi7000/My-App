from emailsender import *
from fastapi import FastAPI
import sqlite3
import hashlib
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import random
import string

connections = {}

global online_emails
online_emails = []

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def list_online_emails(online_emails):
    return online_emails

def Delete_Message_from_user(message_id):
    try:
        conn = sqlite3.connect('My-App/My-App/user_database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chatmessages WHERE message_id=?", (message_id,))
        conn.commit()
        cursor.close()
        return True
    
    except Exception as e:
        print(e)
        return False

def add_email_to_online(email, online_list):
    if email in online_list:
        return
    else:
        online_list.append(email)

def delete_email_from_online(email, online_list):
    if email in online_list:
        online_list.remove(email)
    else:
        return

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

def get_chat_messages(user_id: str, friend_id: str):
    conn = sqlite3.connect('My-App/My-App/user_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (user_id,))

    user_result = cursor.fetchone()

    cursor.execute('''
        SELECT id FROM users
        WHERE email = ?
    ''', (friend_id,))

    friend_result = cursor.fetchone()

    if user_result is None or friend_result is None:
        return {
            "messages": []
        }

    user_id = str(user_result[0])
    friend_id = str(friend_result[0])

    cursor.execute('''
        SELECT
            message,
            timestamp,
            sending_user.email AS sending_user_email,
            receiving_user.email AS receiving_user_email,
            message_id
        FROM chatmessages
        JOIN users sending_user ON sending_user.id=chatmessages.user_id
        JOIN users receiving_user ON receiving_user.id=chatmessages.friend_id
        WHERE (chatmessages.user_id = ? AND chatmessages.friend_id = ?)
            OR (chatmessages.friend_id = ? AND chatmessages.user_id = ?)
        ORDER BY timestamp ASC
    ''', (user_id, friend_id, user_id, friend_id))

    messages = cursor.fetchall()
    
    formatted_messages = [
        {
            "text": message[0],
            "timestamp": message[1],
            "sending_user": message[2],
            "receiving_user": message[3],
            "message_id": message[4]
        }
        for message in messages
    ]

    return {
        "messages": formatted_messages
    }

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
        return friend_list
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
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            view INT NOT NULL DEFAULT 0
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

    SendRegistrationMail(email=email)
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
            SendReminderLoginMail(email=email)
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


@app.get("/GetAllFriends/{email_id}")
def AddToFriendList(email_id):
    friends = get_friend_list(email=email_id)
    jsonstring = {
        "friends": friends
    }
    return jsonstring

@app.post("/ResetPassword/{email}")
def ResetPassword(email):
    code = generate_random_string(length=6)
    ResetPasswortEmail(email=email, code=code)
    jsonstring = {
        "code": code
    }
    return jsonstring

@app.post("/DeleteMesssage/{message_id}")
def DeleteMessage(message_id):
    Delete_Status = Delete_Message_from_user(message_id=message_id)
    if Delete_Status:
        jsonstring = {
        "message_id": message_id
    }
        return jsonstring
    elif Delete_Status == False:
        jsonstring = {
            "message_id": None
        }
        return jsonstring
@app.post("/resetpassword/{password}")
def resetpassword(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    update_password(hashed_password)
    return
@app.websocket("/gettext/{user_id}/{friend_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, friend_id: str):
    await websocket.accept()
    try:
        while True:
            messages = get_chat_messages(user_id=user_id, friend_id=friend_id)
            await websocket.send_json(messages)


    except Exception as e:
        print(f"WebSocket closed with exception: {e}")


@app.websocket("/sendtext/{user_id}/{friend_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, friend_id: str):
    await websocket.accept()
    try:
        while True:
            user_message = await websocket.receive_text()
            save_chat_messages(user_id=user_id, friend_id=friend_id, chat_message=user_message)
            jsonstring = {
        "messages": user_message
     }
            await websocket.send_json(jsonstring)
            
    except Exception as e:
        print(f"WebSocket closed with exception: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)