import sys
import json

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QTabWidget, QMessageBox
)

MODULE_DIR = "server/users.txt"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VirtualLab")
        self.resize(280, 160)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.clicked.connect(self.login)

        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("Nombre")
        self.id_in = QLineEdit()
        self.id_in.setPlaceholderText("ID")
        self.pass_in = QLineEdit()
        self.pass_in.setPlaceholderText("Contraseña")
        self.btn_register = QPushButton("Registrarse")
        self.btn_register.clicked.connect(self.register)

        self.tabs = QTabWidget()
        self.tab_login = QWidget()
        self.tab_register = QWidget()

        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.id_input)
        vbox1.addWidget(self.pass_input)
        vbox1.addWidget(self.btn_login)
        self.tab_login.setLayout(vbox1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.name_in)
        vbox2.addWidget(self.id_in)
        vbox2.addWidget(self.pass_in)
        vbox2.addWidget(self.btn_register)
        self.tab_register.setLayout(vbox2)

        self.tabs.addTab(self.tab_login, "Iniciar sesión")
        self.tabs.addTab(self.tab_register, "Registrarse")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def login(self):
        with open(MODULE_DIR, "r", encoding="utf-8") as f:
            for line in f:
                user = json.loads(line)
                if user["id"] == self.id_input.text() and user["password"] == self.pass_input.text():
                    import gui_labs
                    self.labs_window = gui_labs.LabsWindow(user)
                    self.labs_window.show()
                    self.hide()
                    return
        QMessageBox.warning(self, "Error", "ID o contraseña incorrectos")

    def register(self):
        if not self.name_in.text() or not self.id_in.text() or not self.pass_in.text():
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return
        new_user = {
            "name": self.name_in.text(),
            "id": self.id_in.text(),
            "role": "student",
            "password": self.pass_in.text()
        }
        with open(MODULE_DIR, "a", encoding="utf-8") as f:
            f.write(json.dumps(new_user) + "\n")
        QMessageBox.information(self, "Registrado", "Usuario registrado con éxito")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
