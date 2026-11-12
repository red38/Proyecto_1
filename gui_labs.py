import sys
import os
import json
import zipfile

from PyQt5.QtWidgets import (
    QApplication, QWidget, QListWidget, QPushButton, QLabel,
    QVBoxLayout, QMessageBox, QFileDialog, QDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PySpice.Spice.Parser import SpiceParser

import virtuallab_client as backend

SERVER_URL = "http://localhost:80"


def simulate(cir_text, lab_name):
    print(f"=== Simulacion {lab_name} ===")

    try:
        parser = SpiceParser(source=cir_text)
        circuit = parser.build_circuit()
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        has_capacitor = any(line.strip().upper().startswith("C") for line in cir_text.splitlines())

        if has_capacitor:
            print("Análisis transitorio")
            simulator.transient(step_time=1e-3, end_time=1e-2)
        else:
            print("Análisis DC")
            simulator.operating_point()

        print("Simulación completada con PySpice")
    except Exception as exc:
        raise RuntimeError(f"No se pudo simular el circuito: {exc}") from exc


class LabsWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.is_professor = user.get("role") == "professor"
        if self.is_professor:
            self.setWindowTitle(f"Laboratorios (Profesor) - {user['name']}")
        else:
            self.setWindowTitle(f"Laboratorios - {user['name']}")
        self.resize(400, 320)

        self.lab_list = QListWidget()
        self.lab_list.itemClicked.connect(self.load_lab)
        self.load_labs()

        self.image_label = QLabel("Sin imagen")
        self.image_label.setFixedHeight(190)
        self.image_label.setStyleSheet("border: 1px solid #aaa; background: white;")

        self.btn_run = QPushButton("Correr simulación")
        self.btn_run.clicked.connect(self.run_simulation)

        self.cir_text = None
        self.has_image = False

        layout = QVBoxLayout()
        layout.addWidget(self.lab_list)
        layout.addWidget(self.image_label)
        layout.addWidget(self.btn_run)

        if self.is_professor:
            self.btn_upload = QPushButton("Subir laboratorio")
            self.btn_upload.clicked.connect(self.upload_lab)
            self.btn_assign = QPushButton("Asignar laboratorio")
            self.btn_assign.clicked.connect(self.assign_lab)
            layout.addWidget(self.btn_upload)
            layout.addWidget(self.btn_assign)

        self.cir_text = None
        self.has_image = False

        self.setLayout(layout)

    def load_labs(self):
        if self.is_professor:
            response = backend.listProfessorsLabs(SERVER_URL, self.user["id"])
        else:
            response = backend.listStudentLabs(SERVER_URL, self.user["id"])
        try:
            labs = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            QMessageBox.warning(self, "Error", f"No se pudieron listar los labs:\n{response}")
            return
        if not isinstance(labs, list) or not labs:
            return
        for lab in labs:
            self.lab_list.addItem(self.normal(lab))

    def normal(self, lab):
        return str(lab).replace(".zip", "")

    def load_lab(self, item):
        self.cir_text = None
        self.has_image = False
        response = backend.downloadLab(SERVER_URL, self.user["id"], item.text() + ".zip")
        zip_path = os.path.join("client", "labs", item.text() + ".zip")
        try:
            with zipfile.ZipFile(zip_path) as archive:
                for name in archive.namelist():
                    base = os.path.basename(name)
                    if base.endswith((".cir",)):
                        self.cir_text = archive.read(name).decode("utf-8")
                    elif base.endswith((".png", ".jpg", ".jpeg")):
                        pixmap = QPixmap()
                        pixmap.loadFromData(archive.read(name))
                        self.has_image = True
                        self.image_label.setPixmap(
                            pixmap.scaled(self.image_label.width(),
                                          self.image_label.height(),
                                          Qt.KeepAspectRatio))
                if self.cir_text is None:
                    QMessageBox.warning(self, "Error", "El laboratorio no tiene circuito")
                if not self.has_image:
                    self.image_label.setText("Sin imagen")
        except (FileNotFoundError, zipfile.BadZipFile):
            QMessageBox.warning(self, "Error", response)

    def run_simulation(self):
        selected = self.lab_list.currentItem()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un laboratorio")
            return
        if self.cir_text is None:
            QMessageBox.warning(self, "Error", "Carga el laboratorio con clic")
            return
        try:
            simulate(self.cir_text, selected.text())
        except RuntimeError as exc:
            QMessageBox.warning(self, "Error", str(exc))

    def upload_lab(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un laboratorio", "", "Laboratorios (*.zip)")
        if not file_path:
            return
        response = backend.uploadLab(SERVER_URL, self.user["id"], file_path)
        if "succesfully received" in response:
            QMessageBox.information(self, "Subido", "Laboratorio subido con éxito")
            self.lab_list.clear()
            self.load_labs()
        else:
            QMessageBox.warning(self, "Error", response)

    def assign_lab(self):
        lab_item = self.lab_list.currentItem()
        if lab_item is None:
            QMessageBox.warning(self, "Error", "Selecciona un laboratorio")
            return
        lab_name = lab_item.text()

        response = backend.listStudents(SERVER_URL, self.user["id"])
        try:
            students = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            students = []
        if not isinstance(students, list) or not students:
            QMessageBox.warning(self, "Error", "No hay estudiantes registrados")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Asignar {lab_name}")
        dialog.resize(260, 300)
        student_list = QListWidget(dialog)
        for student in students:
            student_list.addItem(str(student))
        btn_ok = QPushButton("Asignar", dialog)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Selecciona un estudiante:"))
        vbox.addWidget(student_list)
        vbox.addWidget(btn_ok)
        dialog.setLayout(vbox)

        def do_assign():
            student_item = student_list.currentItem()
            if student_item is None:
                QMessageBox.warning(dialog, "Error", "Selecciona un estudiante")
                return
            response = backend.assignLab(
                SERVER_URL, self.user["id"], lab_name, student_item.text())
            if "error" in response:
                QMessageBox.warning(dialog, "Error", response)
            else:
                dialog.accept()
                QMessageBox.information(
                    self, "Asignado",
                    f"Laboratorio {lab_name} asignado a {student_item.text()}")

        btn_ok.clicked.connect(do_assign)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabsWindow({"name": "Prueba", "id": "8888"})
    window.show()
    sys.exit(app.exec_())
