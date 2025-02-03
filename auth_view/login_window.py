# login_window.py
import qtawesome as qta
from PySide6.QtWidgets import (
    QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from auth_view.signup_window import AuthWindow
from backend_controller import db_handler
from Message_app_view.message_view import MainWindow
from helpers.log_message import LogMessage
from sessions.User import User





class LoginWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        self.signup_window = None
        self.setWindowTitle("Login to ChatHub")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #2c3e50;")
        self.message = LogMessage()
        self.message_window = None

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Logo
        logo_label = QLabel()
        logo_label.setPixmap(qta.icon("fa.user-circle", color="#1abc9c").pixmap(80, 80))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title = QLabel("Welcome Back to ChatHub")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Login to access your account.")
        subtitle.setStyleSheet("font-size: 18px; color: #bdc3c7; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Email input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setStyleSheet(
            "font-size: 18px; padding: 10px; border: 2px solid white; border-radius: 5px; color: white; background-color: #34495e;"
        )
        layout.addWidget(self.name_input)

        # Password input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter your phone number")
        self.phone_input.setStyleSheet(
            "font-size: 18px; padding: 10px; border: 2px solid white; border-radius: 5px; color: white; background-color: #34495e;"
        )
        layout.addWidget(self.phone_input)

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(
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
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        # Link-like button for "Forgot Password?"
        link_label = QPushButton("Don't have an account?")
        link_label.setStyleSheet(
            "font-size: 16px; color: #1abc9c; background: none; border: none; text-decoration: underline; cursor: pointer;"
        )
        link_label.setCursor(Qt.PointingHandCursor)

        link_label.clicked.connect(self.open_signup_window)

        layout.addWidget(link_label, alignment=Qt.AlignCenter)

        # Set the central widget
        self.setCentralWidget(central_widget)

    def open_signup_window(self):
        # Create and show the login window if not already created
        if self.signup_window is None:
            self.signup_window = AuthWindow()

        self.signup_window.show()
        self.close()

    def handle_login(self):
        """Handle user login logic."""
        name = self.name_input.text().strip()
        phone_number = self.phone_input.text().strip()

        if not name or not phone_number:
            self.message.show_error_message("Name or phone number cannot be empty.")
            return

        if db_handler.login_user(name, phone_number):
            self.message.show_success_message("Login successful!")


            #Establishing a session
            user = User(name, phone_number)
            user.set_name(name)
            user.set_phone_number(phone_number)

            #get user id
            user_id = db_handler.fetch_user_id(name, phone_number)
            user.set_user_id(user_id)


            # self.message.clear_inputs(self.name_input, self.phone_input)

            #showing the message window after login
            self.message_window = MainWindow(name, phone_number, user_id)
            self.message_window.show()
            self.close()

        else:
           self.message.show_error_message("Invalid name or phone number. Please try again.")