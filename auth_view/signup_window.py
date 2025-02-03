# signup_window.py
import qtawesome as qta
from PySide6.QtWidgets import (
    QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from auth_view import login_window #avoiding circular imports
from backend_controller import db_handler
from helpers.log_message import LogMessage


class AuthWindow(QMainWindow):

    navigate_to_login = Signal()

    def __init__(self):
        """
        Initializes the AuthWindow class, setting up the main window for user
        account registration. This includes setting the window properties such as
        title, size, and style. It also configures the central widget layout with
        a logo, title, subtitle, input fields for name and phone number, a submit
        button, and a link to navigate to the login window.

        The window is styled with a modern look using QtAwesome icons and custom
        stylesheets for each widget component.
        """
        super().__init__()
        self.login_window = None
        self.setWindowTitle("Signup with ChatHub")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #2c3e50;")
        self.message = LogMessage()


        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Logo (optional) - You can replace this with an actual logo image if needed
        logo_label = QLabel()
        logo_label.setPixmap(qta.icon("fa.comment", color="#1abc9c").pixmap(80, 80))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Modern Title at the top center
        title = QLabel("ChatHub - Stay Connected")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Enter your details to get started!")
        subtitle.setStyleSheet("font-size: 18px; color: #bdc3c7; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setStyleSheet(
            "font-size: 18px; padding: 10px; border: 2px solid white; border-radius: 5px; color: white; background-color: #34495e;"
        )
        layout.addWidget(self.name_input)

        # Phone number input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter your phone number")
        self.phone_input.setStyleSheet(
            "font-size: 18px; padding: 10px; border: 2px solid white; border-radius: 5px; color: white; background-color: #34495e;"
        )
        layout.addWidget(self.phone_input)


        # Submit Button
        submit_btn = QPushButton("Create Account")
        submit_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 18px; font-weight: bold; color: white;
                background-color: #1abc9c; border: none; border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QPushButton:pressed {
                background-color: #149174;
            }
            """
        )
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_signup)
        layout.addWidget(submit_btn)


        # Link-like button for "Already have an account?" or "Forgot number?"
        link_label = QPushButton("Already have an account?")
        link_label.setStyleSheet(
            "font-size: 16px; color: #1abc9c; background: none; border: none; text-decoration: underline; cursor: pointer;"
        )
        link_label.setCursor(Qt.PointingHandCursor)
        link_label.clicked.connect(self.open_login_window)
        layout.addWidget(link_label, alignment=Qt.AlignCenter)

        # Set the central widget
        self.setCentralWidget(central_widget)

    def open_login_window(self):
        # Create and show the login window if not already created
        if self.login_window is None:
            self.login_window = login_window.LoginWindow()

        self.login_window.show()
        self.close()

    def handle_signup(self):
        """Handle user signup logic."""
        name = self.name_input.text().strip()  # Access the name input
        phone_number = self.phone_input.text().strip()  # Access the phone input

        # Validate user input
        is_valid, error_message = db_handler.validate_user_data(name, phone_number)
        if not is_valid:
            self.message.show_error_message(error_message)
            return

        # Check if the user already exists in the database
        if db_handler.check_user_exists(name, phone_number):
            self.message.show_error_message("An account with this name or phone number already exists.")
            return

        # Insert user into the database
        db_handler.insert_user(name, phone_number)
        self.message.show_success_message("Account created successfully!")
        self.message.clear_inputs(self.name_input, self.phone_input)


