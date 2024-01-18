import flet as ft
import requests
import json
import re

def is_string(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    match = re.match(pattern, email)
    
    return bool(match)

def main(page: ft.Page):

    def Login_Page(e=None):
        page.clean()
        def login(e):
            login_api = f'http://127.0.0.1:8000/LoginIntoAaccount/{Email_register.value},{Password_register.value}'
            return_from_api_login = requests.get(login_api)
            jsonreturn = json.loads(return_from_api_login.text)
            status_text_bar.value = f"Status: {jsonreturn['status']}"
            page.update()
            if jsonreturn["bool"] == True:
                page.client_storage.set("email", Email_register.value)

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
                return_from_api_register = requests.get(register_api)
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
            print(value)
            if value == None:
                Register_Page()
        except:
            Register_Page()

    PageOnLoad()
ft.app(target=main)