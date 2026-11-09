import sys
import os
import re
import zipfile
import math

from PyQt5.QtWidgets import (
    QApplication, QWidget, QListWidget, QPushButton, QLabel,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

LABS_DIR = "client/labs"


def value(s):
    m = re.match(r"([0-9.]+)", s)
    n = float(m.group(1))
    suffix = s[m.end():]
    mult = {"k": 1e3, "K": 1e3, "M": 1e6, "m": 1e-3,
            "u": 1e-6, "n": 1e-9, "p": 1e-12, "g": 1e9}
    if suffix and suffix[0] in mult:
        n *= mult[suffix[0]]
    return n


def solve(matrix, vector):
    n = len(vector)
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(matrix[r][i]))
        matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
        vector[i], vector[pivot] = vector[pivot], vector[i]
        for r in range(i + 1, n):
            factor = matrix[r][i] / matrix[i][i]
            for c in range(i, n):
                matrix[r][c] -= factor * matrix[i][c]
            vector[r] -= factor * vector[i]
    x = [0.0] * n
    for i in reversed(range(n)):
        acc = vector[i] - sum(matrix[i][c] * x[c] for c in range(i + 1, n))
        x[i] = acc / matrix[i][i]
    return x


def parse_cir(cir_text):
    elements = []
    for line in cir_text.splitlines():
        line = line.strip()
        if not line or line[0] in ".*$;#":
            continue
        parts = line.split()
        kind = parts[0][0].upper()
        if kind == "V":
            if "PULSE" in line:
                nums = re.findall(r"[0-9.]+", line.split("(")[1])
                elements.append(("V", parts[1], parts[2],
                                 float(nums[0]), float(nums[1])))
            else:
                elements.append(("V", parts[1], parts[2],
                                 float(parts[-1]), float(parts[-1])))
        elif kind == "R":
            elements.append(("R", parts[1], parts[2], value(parts[-1]), None))
        elif kind == "C":
            elements.append(("C", parts[1], parts[2], value(parts[-1]), None))
    return elements


def simulate(cir_text, lab_name):
    elements = parse_cir(cir_text)
    print(f"=== Simulacion {lab_name} ===")
    print("Componentes:")
    for e in elements:
        print(f"  {e}")

    resistors = [e for e in elements if e[0] == "R"]
    caps = [e for e in elements if e[0] == "C"]
    sources = [e for e in elements if e[0] == "V"]

    if caps and resistors and sources:
        src = sources[0]
        res = resistors[0]
        cap = caps[0]
        tau = res[3] * cap[3]
        v_final = src[4]
        print("Analisis transitorio (Circuito RC)")
        print(f"  tau = R1 * C1 = {tau:.6f} s")
        print(f"  Vout(t) = {v_final:.2f} * (1 - e^(-t/tau))")
        print("      t (s)   Vout (V)")
        for step in range(0, 6):
            t = step * tau
            vout = v_final * (1 - math.exp(-t / tau))
            print(f"  {t:10.6f} {vout:10.4f}")
        return

    known = {}
    for src in sources:
        if src[3] == src[4] and src[2] == "0":
            known[src[1]] = src[3]

    unknowns = sorted({n for r in resistors for n in (r[1], r[2])
                       if n != "0" and n not in known})
    index = {node: i for i, node in enumerate(unknowns)}
    n = len(unknowns)
    matrix = [[0.0] * n for _ in range(n)]
    vector = [0.0] * n
    for res in resistors:
        conductance = 1.0 / res[3]
        a, b = res[1], res[2]
        a_known = a in known or a == "0"
        b_known = b in known or b == "0"
        if a_known and b_known:
            continue
        if a_known:
            matrix[index[b]][index[b]] += conductance
            vector[index[b]] += known.get(a, 0.0) * conductance
        elif b_known:
            matrix[index[a]][index[a]] += conductance
            vector[index[a]] += known.get(b, 0.0) * conductance
        else:
            matrix[index[a]][index[a]] += conductance
            matrix[index[b]][index[b]] += conductance
            matrix[index[a]][index[b]] -= conductance
            matrix[index[b]][index[a]] -= conductance
    voltages = solve(matrix, vector)

    print("Analisis DC (Divisor de voltaje)")
    for node, pos in index.items():
        print(f"  {node} = {voltages[pos]:.4f} V")


class LabsWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Laboratorios - {user['name']}")
        self.resize(400, 320)

        self.lab_list = QListWidget()
        self.lab_list.itemClicked.connect(self.load_lab)
        self.load_labs()

        self.image_label = QLabel("Sin imagen")
        self.image_label.setFixedHeight(190)
        self.image_label.setStyleSheet("border: 1px solid #aaa; background: white;")
        self.image_label.setScaledContents(False)

        self.btn_run = QPushButton("Correr simulación")
        self.btn_run.clicked.connect(self.run_simulation)

        self.cir_text = None

        layout = QVBoxLayout()
        layout.addWidget(self.lab_list)
        layout.addWidget(self.image_label)
        layout.addWidget(self.btn_run)
        self.setLayout(layout)

    def load_labs(self):
        if os.path.exists(LABS_DIR):
            for file in sorted(os.listdir(LABS_DIR)):
                if file.endswith(".zip"):
                    self.lab_list.addItem(file.replace(".zip", ""))

    def load_lab(self, item):
        zip_path = os.path.join(LABS_DIR, item.text() + ".zip")
        self.cir_text = None
        self.has_image = False
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
            QMessageBox.warning(self, "Error", f"No se pudo cargar {item.text()}.zip")
            self.image_label.setText("Sin imagen")

    def run_simulation(self):
        selected = self.lab_list.currentItem()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un laboratorio")
            return
        if self.cir_text is None:
            QMessageBox.warning(self, "Error", "Cargaste un laboratorio sin circuito")
            return
        simulate(self.cir_text, selected.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabsWindow({"name": "Prueba"})
    window.show()
    sys.exit(app.exec_())
