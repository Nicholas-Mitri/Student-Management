from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize
import sys, sqlite3 as sql


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(QSize(800, 600))  # Set initial window size

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.add_student)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def add_student(self):
        dialog = InsertDialog()
        dialog.exec()

    def load_data(self):
        connection = sql.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )
        connection.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedSize(QSize(300, 300))
        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        self.course_name.addItems(["Biology", "Math", "Astronomy", "Physics"])
        layout.addWidget(self.course_name)

        self.mobile_name = QLineEdit()
        self.mobile_name.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_name)

        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        with sql.connect("database.db") as connection:
            cursor = connection.cursor()
            name = self.student_name.text()
            course = self.course_name.itemText(self.course_name.currentIndex())
            mobile = self.mobile_name.text()
            try:
                cursor.execute(
                    "INSERT INTO students (name, course, mobile) Values (?,?,?)",
                    (name, course, mobile),
                )
                connection.commit()
            except Exception as e:
                print(f"Error inserting student: {e}")
                connection.rollback()
            finally:
                cursor.close()
        main_window.load_data()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
