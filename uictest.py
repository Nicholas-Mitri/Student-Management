from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi("form.ui", self)

        # Now you can access widgets using their object names from the UI file
        # For example, if you have a button named 'pushButton' in your UI:
        # self.pushButton.clicked.connect(self.button_clicked)

        # Example of setting properties
        # self.setWindowTitle("My Application")
        # if you have a label: self.label.setText("New Text")

    # Add your custom methods here
    def button_clicked(self):
        print("Button was clicked!")

    # You can add more methods to handle other widgets


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
