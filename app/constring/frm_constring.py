"""using flet UI to Build connection string for SQL Server."""

import flet as ft


class ConStringBuilderForm(ft.Column):
    def __init__(self):
        super().__init__()
        self.drd_auth_mode = ft.Dropdown(
            options=[
                ft.dropdown.Option("SQL Server Authentication"),
                ft.dropdown.Option("Windows Authentication"),
            ],
            label="Authentication Mode",
            value="SQL Server Authentication",
            width=300,
        )
        self.txt_servername = ft.TextField(label="Server Name", width=300)
        self.txt_database = ft.TextField(label="Database Name", width=300)
        self.txt_uid = ft.TextField(label="User ID", width=300, disabled=False)
        self.txt_pwd = ft.TextField(
            label="Password",
            width=300,
            password=True,
            disabled=False,
            can_reveal_password=True,
        )
        self.chk_mars = ft.Checkbox(
            label="Enable MARS (Multiple Active Result Sets)", value=True
        )
        self.chk_encrypt = ft.Checkbox(label="Encrypt Connection", value=True)
        self.txt_constring = ft.TextField(
            label="Connection String",
            multiline=True,
            min_lines=5,
            max_lines=10,
            width=400,
        )
        self.btn_testconn = ft.ElevatedButton(text="Test Connection")
        self.btn_save = ft.ElevatedButton(text="Save")
        self.btn_cancel = ft.ElevatedButton(text="Cancel")

        self.controls = [
            self.drd_auth_mode,
            self.txt_servername,
            self.txt_database,
            self.txt_uid,
            self.txt_pwd,
            self.chk_mars,
            self.chk_encrypt,
            self.btn_testconn,
            ft.Row([self.btn_save, self.btn_cancel]),
            self.txt_constring,
        ]

    def build_constring(self, e=None):
        parts = []
        if self.txt_servername.value:
            parts.append(f"Server={self.txt_servername.value}")
        if self.txt_database.value:
            parts.append(f"Database={self.txt_database.value}")
        if self.drd_auth_mode.value == "Windows Authentication":
            parts.append("Trusted_Connection=yes")
        else:
            if self.txt_uid.value:
                parts.append(f"UID={self.txt_uid.value}")
            if self.txt_pwd.value:
                parts.append(f"PWD={self.txt_pwd.value}")
            parts.append("Trusted_Connection=no")
        parts.append(f"MARS_Connection={'Yes' if self.chk_mars.value else 'No'}")
        parts.append(f"Encrypt={'Yes' if self.chk_encrypt.value else 'No'}")
        con_str = ";".join(parts)
        self.txt_constring.value = con_str
        self.txt_constring.update()
        self.update()

    def on_auth_mode_change(self, e=None):
        if self.drd_auth_mode.value == "Windows Authentication":
            self.txt_uid.value = ""
            self.txt_pwd.value = ""
            self.txt_uid.disabled = True
            self.txt_pwd.disabled = True
        else:
            self.txt_uid.disabled = False
            self.txt_pwd.disabled = False
        self.txt_uid.update()
        self.txt_pwd.update()
        self.update()

    def on_save(self, e=None):
        # Copy connection string to clipboard
        self.page.set_clipboard(
            self.txt_constring.value if self.txt_constring.value is not None else ""
        )

    def on_cancel(self, e=None):
        self.drd_auth_mode.value = "SQL Server Authentication"
        self.txt_servername.value = ""
        self.txt_database.value = ""
        self.txt_uid.value = ""
        self.txt_pwd.value = ""
        self.chk_mars.value = True
        self.chk_encrypt.value = True
        self.txt_constring.value = ""
        self.drd_auth_mode.update()
        self.txt_servername.update()
        self.txt_database.update()
        self.txt_uid.update()
        self.txt_pwd.update()
        self.chk_mars.update()
        self.chk_encrypt.update()
        self.txt_constring.update()
        self.on_auth_mode_change(None)
        self.update()

    def build(self):
        self.drd_auth_mode.on_change = self.on_auth_mode_change
        self.btn_testconn.on_click = self.build_constring
        self.btn_save.on_click = self.on_save
        self.btn_cancel.on_click = self.on_cancel
        self.on_auth_mode_change(None)


def main(page: ft.Page):
    page.title = "Connection String Builder for SQL Server"
    page.add(ConStringBuilderForm())


if __name__ == "__main__":
    ft.app(target=main)
