import flet as ft
import requests
import json
import re
import time

def is_string(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    match = re.match(pattern, email)
    
    return bool(match)

def main(page: ft.Page):
    def SearchOnlineUsers_Page(e):
        def AddUserToFriendList(e):
            print(e.control.data)
            requests.post(f"http://127.0.0.1:8000/AddToFriendList/{page.client_storage.get('email')},{e.control.data}")


        page.clean()
        OnlineUserList = requests.get("http://127.0.0.1:8000/ListOnlineUsers")
        jsonreturn = json.loads(OnlineUserList.text)
        for user in jsonreturn["onlineusers"]:
            ListOnlineUser = ft.TextButton(text=f"Add: {user}", on_click=AddUserToFriendList, data=user)
            page.add(ListOnlineUser)

    def Home_Page(e=None):
        requests.post(f"http://127.0.0.1:8000/OnlineUser/{page.client_storage.get('email')}")
        page.clean()
        def LogOut(e):
            page.client_storage.remove("email")
            Register_Page()

        NavigationBar = ft.AppBar(
            leading=ft.Icon(ft.icons.PALETTE),
            leading_width=40,
            title=ft.Text(f"Welcome {page.client_storage.get('email')}"),
            center_title=False,

            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.icons.WB_SUNNY_OUTLINED),
                ft.IconButton(ft.icons.FILTER_3),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Log out", checked=False, on_click=LogOut
                        ),
                        ft.PopupMenuItem(
                            text="Search Online Users", checked=False, on_click=SearchOnlineUsers_Page
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
                time.sleep(2)
                Home_Page()

        status_text_bar = ft.Text()    
        Email_register = ft.TextField(label="Email")    
        Password_register = ft.TextField(label="Password", password=True, can_reveal_password=True)
        Register_Sumbit = ft.ElevatedButton(text="Login", on_click=login)

        page.add(Email_register, Password_register, Register_Sumbit, status_text_bar)

        Register_Link = ft.TextButton("Register", on_click=Register_Page)
        page.add(Register_Link)

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

        Login_Link = ft.TextButton("Login", on_click=Login_Page)


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