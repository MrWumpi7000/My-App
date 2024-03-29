import flet as ft
import requests
import json
import re
import time
from pytube import YouTube
import asyncio
import websockets
import hashlib
import tracemalloc
from websocket import create_connection
from datetime import datetime
from dataclasses import dataclass
import string
import random
import os
import keyboard
from pathlib import Path

tracemalloc.start()

@dataclass
class Messageclass:
    user: str
    text: str
    timestamp: datetime

def download_youtube_video(link, e = None):
    try:
        yt = YouTube(link)
        output_path = os.path.join(os.path.dirname(__file__), yt.title + '.mp4')
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video_stream.download(output_path=output_path)
        print("Download completed successfully!")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def combine_and_hash(str1, str2):
    combined_string = ''.join(sorted([str1, str2]))
    hashed_result = hashlib.sha256(combined_string.encode()).hexdigest()
    return hashed_result

def get_initials(user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

def get_avatar_color(user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

def is_string(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    match = re.match(pattern, email)
    
    return bool(match)

def main(page: ft.Page):
    def Download_video_page(e = None):
        def button_clicked(e):
            print("click")
            download_youtube_video(youtube_input_link.value)
        page.clean()
        Heading = ft.Text("Hey, put in your download link into the input field to download your video!")
        youtube_input_link = ft.TextField(label="Standard")
        download_link_sumbit = ft.ElevatedButton(text="Submit", on_click=button_clicked)
        page.add(Heading, youtube_input_link, download_link_sumbit)
    def Tools_Page(e = None):
        page.clean()
        rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
      #  extended=True,
        min_width=100,
        min_extended_width=400,
        #leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Add"),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.FAVORITE_BORDER, selected_icon=ft.icons.FAVORITE, label="First"
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.BOOKMARK_BORDER),
                selected_icon_content=ft.Icon(ft.icons.BOOKMARK),
                label="Second",
                
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label_content=ft.Text("Settings"),
            ),
        ],
    on_change = lambda e: (Download_video_page() if e.control.selected_index == 0 else (Tools_Page() if e.control.selected_index == 1 else (Tools_Page() if e.control.selected_index == 2 else None)))
    )

        page.add(
            ft.Row(
                [
                    rail,
                    ft.VerticalDivider(width=1),
                    ft.Column([ ft.Text("Body!")], alignment=ft.MainAxisAlignment.START, expand=True),
                ],
                expand=True,
            )
        )

    def upload_image(image_path):
        upload_endpoint = f"http://0.0.0.0:8000/upload/{page.client_storage.get('email')}"
        try:
            with open(image_path, "rb") as file:
                filename = image_path.split('/')[-1]
                files = {'file': (filename, file, 'image/jpeg')}
                response = requests.post(upload_endpoint, files=files)

            if response.status_code == 200:
                print("Image uploaded successfully!")
                print("Response:", response.json())
                page.clean()
                AccountSettings_Page()
            else:
                print("Failed to upload image:", response.status_code)
                print("Error message:", response.text)
        except Exception as e:
            print("An error occurred:", e)


    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    def Chat_Page(e):
        def chatwithfriend(e):
            page.clean()
            page.scroll = ft.ScrollMode.AUTO
            page.horizontal_alignment = "stretch"
            page.title = f"Friend Chat with {e.control.data}"
            page.update()

            def on_message(topic, message):
                datefromsenduser = message.timestamp
                test = date.fromisoformat(datefromsenduser)
                format_for_chat_pubsub = [
                    ft.CircleAvatar(
                        content=ft.Text(get_initials(message.user)),
                        color=ft.colors.WHITE,
                        bgcolor=get_avatar_color(message.user),
                    ),
                    ft.Column(
                        [
                            ft.Text(f"{message.user} {test.strftime('%m-%d: %H:%M')}Uhr", weight="bold"),
                            ft.Text(message.text, selectable=True),
                        ],
                        tight=True,
                        spacing=5,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ]

                MessageFinnallPubsub = ft.Row(
                    controls=format_for_chat_pubsub,
                    auto_scroll=True,
                    scroll=ft.ScrollMode.AUTO,
                )
                chat.controls.append(MessageFinnallPubsub)
                page.update()

            def SendText(e):
                if MessageText.value.strip() == "":
                    return

                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                wsc = create_connection(f"ws://localhost:8000/sendtext/{page.client_storage.get('email')}/{e.control.data}")
                wsc.send(MessageText.value)
                page.pubsub.send_all_on_topic(combine_and_hash(page.client_storage.get('email'), e.control.data), Messageclass(page.client_storage.get('email'), MessageText.value, dt_string))
                MessageText.value = ""

            def Delete_Message(e):
                Delete_Status = requests.post(f"http://127.0.0.1:8000/DeleteMesssage/{e.control.data['message_id']}")
                print(Delete_Status)
                if e.control.data['receiving_user'] == page.client_storage.get('email'):
                    e.control.data = e.control.data['sending_user']
                else:
                    e.control.data = e.control.data['receiving_user']
                chatwithfriend(e)
                
            print (combine_and_hash(page.client_storage.get('email'), e.control.data))

            page.pubsub.subscribe_topic(combine_and_hash(page.client_storage.get('email'), e.control.data) ,on_message)

            chat = ft.ListView(
                spacing=10, auto_scroll=True
            )

            MessageText = ft.TextField(
                hint_text="Write a message...",
                expand=True,
                autofocus=True,
                shift_enter=True,
                min_lines=1,
                max_lines=5,
                filled=True,
                on_submit=SendText,
                data = e.control.data
            )

            page.add(
                ft.Container(
                    content=chat,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=5,
                    padding=10
                ),
                ft.Row(
                    [
                        MessageText,
                        ft.IconButton(
                            icon=ft.icons.SEND_ROUNDED,
                            on_click=SendText,
                            data = e.control.data
                        ),
                    ]
                ),
            )
            ws = create_connection(f"ws://localhost:8000/gettext/{page.client_storage.get('email')}/{e.control.data}")
            result =  ws.recv()
            jsonreturn = json.loads(result)

            for message in jsonreturn['messages']:
                date = datetime.strptime(message['timestamp'], "%Y-%m-%d %H:%M:%S")
                bla = [
                    ft.CircleAvatar(
                        content=ft.Text(get_initials(message['sending_user'])),
                        color=ft.colors.WHITE,
                        bgcolor=get_avatar_color(message['sending_user']),
                    ),
                    ft.Column(
                        [
                            ft.Text(f"{message['sending_user']} {date.strftime('%m-%d: %H:%M')}Uhr", weight="bold"),
                            ft.Row(
                                [
                                 ft.Text(message['text'], selectable=True),
                                 ft.FilledButton("Delete Message",
                            icon=ft.icons.DELETE_OUTLINE_OUTLINED,
                            on_click= Delete_Message,
                            data = message,
                    
                                )
                    ])],
                        tight=True,
                        spacing=5,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ]

                MessageFinnallPubsub = ft.Row(
                    controls=bla,
                    auto_scroll=True,
                    scroll=ft.ScrollMode.AUTO,
                    data=message['message_id']
                )
                chat.controls.append(MessageFinnallPubsub)
                page.update()
            
        page.clean()
        FriendList = requests.get(f"http://127.0.0.1:8000/GetAllFriends/{page.client_storage.get('email')}")
        jsonreturn = json.loads(FriendList.text)

        for friend in jsonreturn["friends"]:
            FriendChatButton = ft.FilledButton(text=friend, on_click=chatwithfriend, data=friend)
            page.add(FriendChatButton)

    def SearchOnlineUsers_Page(e):
        page.clean()

        def AddUserToFriendList(e):
            print(e.control.data)
            requests.post(f"http://127.0.0.1:8000/AddToFriendList/{page.client_storage.get('email')},{e.control.data}")

        NavigationBar = ft.AppBar(
            leading=ft.Icon(ft.icons.PALETTE),
            leading_width=40,
            title=ft.Text(f"Welcome {page.client_storage.get('email')}"),
            center_title=False,

            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.Text("Online User Page"),
                ft.IconButton(ft.icons.FILTER_3),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Home Page", checked=False, on_click=Home_Page
                        ),
                        ft.PopupMenuItem(
                            text="Chat Page", checked=False, on_click=Chat_Page
                        )
                    ]
                ),
            ],
        )
        page.add(NavigationBar)

        OnlineUserList = requests.get("http://127.0.0.1:8000/ListOnlineUsers")
        jsonreturn = json.loads(OnlineUserList.text)
        for user in jsonreturn["onlineusers"]:
            if user == page.client_storage.get("email"):
                print("Own Email")
            else:
                ListOnlineUser = ft.TextButton(text=f"Add: {user}", on_click=AddUserToFriendList, data=user)
                page.add(ListOnlineUser)

    def AccountSettings_Page(e=None):
        page.clean()
        page.title = f"Account Settings"
        page.horizontal_alignment = page.vertical_alignment = "center"

        bab = ft.BottomAppBar(
        bgcolor=ft.colors.DEEP_PURPLE_300,
        shape=ft.NotchShape.CIRCULAR,
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.icons.HOME, icon_color=ft.colors.WHITE, on_click=Home_Page),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.icons.SEARCH, icon_color=ft.colors.WHITE),
                ft.IconButton(icon=ft.icons.FAVORITE, icon_color=ft.colors.WHITE),
            ]
        ),
    )
        CircleAvater=ft.CircleAvatar(foreground_image_url=f"http://0.0.0.0:8000/get_image/{page.client_storage.get('email')}" ,content=ft.Icon(ft.icons.ABC),radius=100)
        usersname = ft.Text(f"Hello, {page.client_storage.get('email')}", size=20)
     
        def pick_files_result(e: ft.FilePickerResultEvent):
            file_paths = [file_info.path for file_info in e.files]
            print(file_paths)

            if e.files:
                first_file_path = e.files[0].path
                print(first_file_path)
                upload_image(image_path=first_file_path)
            

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        page.overlay.append(pick_files_dialog)

        Upload_Row = ft.ElevatedButton(
                        "Pick files",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=False, file_type="IMAGE"
                        )
                    )
        

        page.add(CircleAvater, usersname, Upload_Row, bab)
        page.update()

    def Home_Page(e=None):
        requests.post(f"http://127.0.0.1:8000/OnlineUser/{page.client_storage.get('email')}")
        page.clean()

        def LogOut(e):
            page.client_storage.remove("email")
            Register_Page()

        NavigationBar = ft.AppBar(
            leading=ft.CircleAvatar(foreground_image_url=f"http://0.0.0.0:8000/get_image/{page.client_storage.get('email')}"),
            color=ft.colors.WHITE,
            leading_width=40,
            title=ft.Text(f"Welcome {page.client_storage.get('email')}", font_family="Helvetica", color="WHITE", weight=ft.FontWeight.BOLD),
            center_title=True,

            bgcolor=ft.colors.DEEP_PURPLE_300,
            actions=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Log out", checked=False, on_click=LogOut
                        ),
                        ft.PopupMenuItem(
                            text="Search Online Users", checked=False, on_click=SearchOnlineUsers_Page
                        ),
                        ft.PopupMenuItem(
                            text="Chat Page", checked=False, on_click=Chat_Page
                        ),
                        ft.PopupMenuItem(
                            text="Tools", checked=False, on_click=Tools_Page
                        ),
                        ft.PopupMenuItem(
                            text="Account Settings", checked=False, on_click=AccountSettings_Page
                        )
                    ]
                ),
            ],
        )
        page.add(NavigationBar)

    def Login_Page(e=None):
        page.clean()
        def login(e):
            login_api = f'http://127.0.0.1:8000/LoginIntoAaccount/{Email_register.value},{Password_register.value}'
            return_from_api_login = requests.post(login_api)
            jsonreturn = json.loads(return_from_api_login.text)
            status_text_bar.value = f"Status: {jsonreturn['status']}"
            page.update()
            if jsonreturn["bool"] == True:
                page.client_storage.set("email", Email_register.value)
                time.sleep(1)
                Home_Page()

        Reset_passwort = ft.OutlinedButton(text="Reset Password", on_click=reset_passwort_page)
        status_text_bar = ft.Text()    
        Email_register = ft.TextField(label="Email")    
        Password_register = ft.TextField(label="Password", password=True, can_reveal_password=True)
        Register_Sumbit = ft.ElevatedButton(text="Login", on_click=login)

        page.add(Email_register, Password_register, Register_Sumbit,Reset_passwort, status_text_bar)

        Register_Link = ft.TextButton("Register Page", on_click=Register_Page)
        page.add(Register_Link)

    def reset_passwort_page(e=None):
        def Reset_Password(e):
            isemailvalidfromresetpassword = requests.post(f'http://127.0.0.1:8000/isemailvalidfrompasswordreserpage/{info_text.value}')
            jsonreturn = json.loads(isemailvalidfromresetpassword.text)
                
            if jsonreturn["bool"] == False:
                emaildoesntexistalert = ft.AlertDialog(
                title=ft.Text("Email doesn't exist"),
                content=ft.Text(f"{info_text.value} doesn't exist, please try a different email"))
                page.dialog = emaildoesntexistalert
                emaildoesntexistalert.open = True
                page.update()
                return
            
            def Final1(e):
                def Final2(e):
                    apiresetpasswordreturnApi = f'http://127.0.0.1:8000/resetpassword/{info_text.value}/{resetInput.value}'
                    requests.post(apiresetpasswordreturnApi)

                    resettedpasswordAlertDialog = ft.AlertDialog(
                    title=ft.Text("Succcess!"),
                    content=ft.Text(f"Your Password has been Resseted and your are now getting redirected to the Home Page!"))
                    page.dialog = resettedpasswordAlertDialog
                    resettedpasswordAlertDialog.open = True
                    page.update()
                    time.sleep(3)
                    Login_Page()

                if reset_passwort.value == e.control.data:
                    page.clean()
                    statustext2 = ft.Text()
                    resetInput = ft.TextField(
                    hint_text="Input the New Password")
                    reset_submit2 = ft.ElevatedButton(text="Reset Your Password", on_click=Final2)
                    page.add(resetInput, reset_submit2, statustext2)
                    
                else:
                    codewaswrong = ft.AlertDialog(
                    title=ft.Text("The Code wasn't right"),
                    content=ft.Text(f"Please try a different one"))
                    page.dialog = codewaswrong
                    codewaswrong.open = True
                    page.update()

            if is_string(info_text.value):
                resetpasswortApi = f'http://127.0.0.1:8000/ResetPassword/{info_text.value}'
                return_from_api_reset = requests.post(resetpasswortApi)
                jsonreturn = json.loads(return_from_api_reset.text)
                statustext.value = f"Status: {jsonreturn['code']}"
                page.clean()
                textfield = ft.Text("Put in the Code from the Email", size=30 )
                reset_passwort = ft.TextField(
                    hint_text="Input the code"
                )
                reset_submit1 = ft.ElevatedButton(text="Sumbit Code", on_click=Final1, data=jsonreturn['code'])
                statustext1 = ft.Text()
                page.add(textfield, reset_passwort, reset_submit1, statustext1)
                
        page.clean()
        info_text = ft.TextField(
            hint_text="Input your Email where the code gets send"
        )
        reset_submit = ft.ElevatedButton(text="Authenticate", on_click=Reset_Password)
        statustext = ft.Text(
        )
        page.add(info_text, reset_submit, statustext)

    def Register_Page(e=None):  
        page.clean()    
        def register(e):
            is_string_answer = is_string(Email_register.value)
            if is_string_answer:
                register_api = f'http://127.0.0.1:8000/RegisterAnewAccount/{Email_register.value},{Password_register.value}'
                return_from_api_register = requests.post(register_api)
                jsonreturn = json.loads(return_from_api_register.text)
                status_text_bar.value = f"Status: {jsonreturn['status']}"
            else:
                status_text_bar.value = f"Status: Please type in a Valid Email"
            page.update()


        status_text_bar = ft.Text()    
        Email_register = ft.TextField(label="Email")    
        Password_register = ft.TextField(label="Password", password=True, can_reveal_password=True)
        Register_Sumbit = ft.ElevatedButton(text="Register", on_click=register)

        page.add(Email_register, Password_register, Register_Sumbit, status_text_bar)

        Login_Link = ft.TextButton("Login Page", on_click=Login_Page)

        page.add(Login_Link)
    
    def PageOnLoad():
        try: 
            value = page.client_storage.get("email")
            if value == None:
                Register_Page()
            else:
                Home_Page()
        except:
            Register_Page()

    PageOnLoad()
ft.app(target=main)