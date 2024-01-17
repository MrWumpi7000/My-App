import flet as ft
import requests
import json

def main(page: ft.Page):

    def Login_Page(e=None):
        page.clean()
        Register_Link = ft.TextButton("Register", on_click=Register_Page)
        page.add(Register_Link)

    def Register_Page(e=None):
        page.clean()    
        def register(e):
            t.value = f"Textboxes values are:  '{Email_register.value}', '{Password_register.value}'."
            page.update()
            register_api = f'http://127.0.0.1:8000/items/{Email_register.value}'
            x = requests.get(register_api)
            test = str(x.text)
            print(test)

            if test == 'Test':
                print(True)


        t = ft.Text()    
        Email_register = ft.TextField(label="Email")    
        Password_register = ft.TextField(label="Password", password=True, can_reveal_password=True)
        Register_Sumbit = ft.ElevatedButton(text="Submit", on_click=register)

        page.add(Email_register, Password_register, Register_Sumbit, t)
        page.add(ft.Text(f"Initial route: {page.route}"))

        Login_Link = ft.TextButton("Login", on_click=Login_Page)


        page.add(Login_Link)
    Register_Page()
ft.app(target=main)