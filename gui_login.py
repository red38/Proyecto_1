import sys
import json

import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QTabWidget, QMessageBox
)

import virtuallab_client as backend

SERVER_URL = "http://localhost:80"


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
        if not self.id_input.text() or not self.pass_input.text():
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return
        response = backend.openSession(SERVER_URL, self.id_input.text(), self.pass_input.text())
        if "succesfully opened" in response:
            # Detectar el rol: listProfessorsLabs solo funciona para profesores
            # con sesión abierta; para un estudiante responde "error...".
            role = "student"
            labs_response = backend.listProfessorsLabs(SERVER_URL, self.id_input.text())
            try:
                if isinstance(json.loads(labs_response), list):
                    role = "professor"
            except (json.JSONDecodeError, ValueError):
                pass
            user = {"name": self.id_input.text(), "id": self.id_input.text(), "role": role}
            import gui_labs
            self.labs_window = gui_labs.LabsWindow(user)
            self.labs_window.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Error", response.replace("error", "ID o contraseña incorrectos"))

    def register(self):
        if not self.name_in.text() or not self.id_in.text() or not self.pass_in.text():
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return
        response = backend.registerUser(SERVER_URL, self.name_in.text(),
                                        self.id_in.text(), "student",
                                        self.pass_in.text())
        if "already registered" in response:
            QMessageBox.warning(self, "Error", "Ese ID ya está registrado")
        else:
            QMessageBox.information(self, "Registrado", "Usuario registrado con éxito")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
