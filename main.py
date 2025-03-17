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
    QToolBar,
    QStatusBar,
    QGroupBox,
    QRadioButton,
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, Qt
import sys, sqlite3 as sql  # Import system and SQLite database modules


class MainWindow(QMainWindow):
    """
    Main application window for the Student Management System.
    Provides interface for viewing, adding, and searching student records.
    """

    def __init__(self):
        """
        Initialize the main window with menus, toolbar, and table widget.
        """
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(QSize(800, 600))  # Set initial window size

        # Create menu bar items
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Create and configure Add Student action
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.add_student)
        file_menu_item.addAction(add_student_action)

        # Create and configure Search action
        search_student_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_student_action.triggered.connect(self.search_student)
        edit_menu_item.addAction(search_student_action)

        # Create and configure About action
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        # Create and configure table widget for displaying student data
        self.table = QTableWidget()
        # Make the table read-only (not editable)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and set it to be movable
        self.toolBar = QToolBar()
        self.toolBar.setMovable(True)

        # Add toolbar to the top of the window and center it
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        # Add actions to the toolbar
        self.toolBar.addAction(add_student_action)
        self.toolBar.addAction(search_student_action)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit_student)

        del_button = QPushButton("Delete Record")
        del_button.clicked.connect(self.del_student)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusBar.removeWidget(child)

        self.statusBar.addWidget(edit_button)
        self.statusBar.addWidget(del_button)

    def del_student(self):
        """
        Delete the selected student from the database and refresh the table.
        """
        selected_row = self.table.currentRow()
        index = int(self.table.item(selected_row, 0).text())
        if selected_row >= 0:
            with sql.connect("database.db") as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        "DELETE FROM students WHERE rowid=?",
                        (index,),
                    )
                    connection.commit()
                except Exception as e:
                    print(f"Error deleting student: {e}")
                    connection.rollback()
                finally:
                    cursor.close()
            self.load_data()

    def edit_student(self):
        """
        Open a dialog to edit the selected student's information.
        """
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            dialog = EditDialog(int(self.table.item(selected_row, 0).text()))
            dialog.exec()

    def add_student(self):
        """
        Open a dialog to add a new student to the database.
        """
        dialog = InsertDialog()
        dialog.exec()

    def search_student(self):
        """
        Open a dialog to search for students by name.
        """
        dialog = SearchDialog()
        dialog.exec()

    def load_data(self):
        """
        Load student data from the database and display it in the table.
        """
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


class EditDialog(QDialog):
    def __init__(self, index=None):
        """
        Initialize the dialog with input fields for student information.
        """
        super().__init__()
        self.setWindowTitle("Edit Student")
        self.setFixedSize(QSize(300, 300))
        layout = QVBoxLayout()

        # Create and add name input field
        self.student_name = QLineEdit()
        layout.addWidget(self.student_name)

        # Create and add course selection dropdown
        self.course_name = QComboBox()
        self.course_name.addItems(["Biology", "Math", "Astronomy", "Physics"])
        layout.addWidget(self.course_name)

        # Create and add mobile number input field
        self.mobile_num = QLineEdit()
        self.mobile_num.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_num)

        # Add status label for error messages
        self.status_label = QLineEdit()
        self.status_label.setReadOnly(True)
        self.status_label.setStyleSheet("color: red;")
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # Populate fields with existing data if index is provided
        self.index = index
        if self.index is not None:
            self.student_name.setText(
                main_window.table.item(main_window.table.currentRow(), 1).text()
            )
            self.course_name.setCurrentText(
                main_window.table.item(main_window.table.currentRow(), 2).text()
            )
            self.mobile_num.setText(
                main_window.table.item(main_window.table.currentRow(), 3).text()
            )

        # Create and add edit button
        button = QPushButton("Edit")
        button.clicked.connect(self.edit_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def edit_student(self):
        """
        Edit information of existing student to the database using the information from the input fields.
        """
        with sql.connect("database.db") as connection:
            cursor = connection.cursor()
            name = self.student_name.text()
            course = self.course_name.itemText(self.course_name.currentIndex())
            mobile = self.mobile_num.text()

            try:
                cursor.execute(
                    "UPDATE students SET name=?, course=?, mobile=? WHERE rowid=?",
                    (name.title(), course.title(), mobile, self.index),
                )
                connection.commit()
                main_window.load_data()
                self.close()
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
                self.status_label.show()
            finally:
                cursor.close()


class InsertDialog(QDialog):
    """
    Dialog for adding a new student to the database.
    """

    def __init__(self):
        """
        Initialize the dialog with input fields for student information.
        """
        super().__init__()
        self.setWindowTitle("Add Student")
        self.setFixedSize(QSize(300, 300))
        layout = QVBoxLayout()

        # Create and add name input field
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create and add course selection dropdown
        self.course_name = QComboBox()
        self.course_name.addItems(["Biology", "Math", "Astronomy", "Physics"])
        layout.addWidget(self.course_name)

        # Create and add mobile number input field
        self.mobile_num = QLineEdit()
        self.mobile_num.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_num)

        # Add status label for error messages
        self.status_label = QLineEdit()
        self.status_label.setReadOnly(True)
        self.status_label.setStyleSheet("color: red;")
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # Create and add register button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        """
        Add a new student to the database using the information from the input fields.
        """
        with sql.connect("database.db") as connection:
            cursor = connection.cursor()
            name = self.student_name.text()
            course = self.course_name.itemText(self.course_name.currentIndex())
            mobile = self.mobile_num.text()
            try:
                cursor.execute(
                    "INSERT INTO students (name, course, mobile) Values (?,?,?)",
                    (name.title(), course.title(), mobile),
                )
                connection.commit()
                main_window.load_data()
                self.close()
            except sql.IntegrityError as e:
                self.status_label.setText(
                    "Error: This mobile number is already registered"
                )
                self.status_label.show()
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
                self.status_label.show()
            finally:
                cursor.close()


class SearchDialog(QDialog):
    """
    Dialog for searching students by name.
    """

    def __init__(self):
        """
        Initialize the dialog with a search input field.
        """
        super().__init__()
        self.setWindowTitle("Student Search")
        self.setFixedSize(QSize(300, 300))
        layout = QVBoxLayout()

        # Create and add name search field
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)
        # Add a spacer to create some vertical space between the search field and button
        layout.addSpacing(20)
        # Create and add search button
        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        layout.addSpacing(10)

        # Create a group box for search options
        search_options = QGroupBox("Search by")
        options_layout = QVBoxLayout()

        # Create radio buttons for search options
        self.id_radio = QRadioButton("ID")
        self.name_radio = QRadioButton("Name")
        self.number_radio = QRadioButton("Mobile Number")

        # Set Name as the default selected option
        self.name_radio.setChecked(True)

        # Add radio buttons to the layout
        options_layout.addWidget(self.id_radio)
        options_layout.addWidget(self.name_radio)
        options_layout.addWidget(self.number_radio)
        # Set spacing between radio buttons to 1
        options_layout.setSpacing(1)

        # Set the layout for the group box
        search_options.setLayout(options_layout)

        # Add the group box to the main layout
        layout.addWidget(search_options)

        self.setLayout(layout)

    def search_student(self):
        """
        Search for students by the selected criteria and highlight matching results in the main table.

        This function retrieves the search text from the input field, determines which column to search
        based on the selected radio button (ID, Name, or Mobile Number), and then highlights any
        matching items in the table. If no matches are found, the table selection is cleared.
        """
        # Clear any existing selection in the table
        main_window.table.clearSelection()
        # Get the search text from the input field
        name = self.student_name.text()
        # Default search column is 1 (Name)
        search_column = 1
        # Change search column based on radio button selection
        if self.id_radio.isChecked():
            search_column = 0  # ID column
        elif self.number_radio.isChecked():
            search_column = 3  # Mobile Number column

        if name:
            # Search for items containing the search text
            items = main_window.table.findItems(name, Qt.MatchFlag.MatchContains)
            if items:
                for item in items:
                    # Only select items that are in the chosen search column
                    if main_window.table.column(item) == search_column:
                        main_window.table.item(item.row(), search_column).setSelected(
                            True
                        )
            else:
                # If no matches found, ensure table has no selection
                main_window.table.clearSelection()


# Create application instance
app = QApplication(sys.argv)
# Create and show main window
main_window = MainWindow()
main_window.show()
# Load initial data
main_window.load_data()
# Start application event loop
sys.exit(app.exec())
