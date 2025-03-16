from PyQt6.QtWidgets import QApplication
from PyQt6 import uic

app = QApplication([])

# Load UI file
window = uic.loadUi("untitled/form.ui")
window.show()
app.exec()
