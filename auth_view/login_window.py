# login_window.py
from PySide6.QtWidgets import (
    QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel, QPushButton
)
from PySide6.QtCore import Qt
import qtawesome as qta

from auth_view.signup_window import AuthWindow


class LoginWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        self.signup_window = None
        self.setWindowTitle("Login to ChatHub")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #2c3e50;")


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
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter your name")
        name_input.setStyleSheet(
            "font-size: 18px; padding: 10px; border: 2px solid white; border-radius: 5px; color: white; background-color: #34495e;"
        )
        layout.addWidget(name_input)

        # Password input
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Enter your phone number")
        phone_input.setStyleSheet(
            "font-size: 18px; padding: 10px; border: 2px solid white; border-radius: 5px; color: white; background-color: #34495e;"
        )
        layout.addWidget(phone_input)

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

