# splash_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

class SplashWindow(QWidget):
    # Define a custom signal that will be emitted when the user clicks continue.
    continueClicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Splash - ChatHub")
        self.setStyleSheet("background-color: #2c3e50;")
        self.setFixedSize(900, 600)

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Logo at the top center
        self.logo = QLabel()
        pixmap = QPixmap("assets/logo.jpg")
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo.setText("Logo not found")
            self.logo.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(self.logo, alignment=Qt.AlignHCenter)

        # Grand welcome message in the middle
        welcome_text = QLabel("Welcome to ChatHub\nYour Secure and Private Messaging Platform\nChat Made Easy")
        welcome_text.setStyleSheet("color: white; font-size: 30px; font-weight: bold;")
        welcome_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_text)

        # Continue link/button
        self.continue_btn = QPushButton("Click here to continue")
        self.continue_btn.setStyleSheet("""
                    QPushButton {
                        color: #3498db;
                        background-color: transparent;
                        border: none;
                        font-size: 20px;
                        text-decoration: underline;
                    }
                    QPushButton:hover {
                        color: #2980b9;
                    }
                """)
        # When the button is clicked, emit our custom signal.
        self.continue_btn.clicked.connect(self.continueClicked.emit)
        layout.addWidget(self.continue_btn, alignment=Qt.AlignCenter)

        # Add stretch to push the footer to the bottom
        layout.addStretch()

        # Developer name as footer
        self.dev_name = QLabel("Developer: By Fanyi Charllson - Full Stack Developer\nCopyright  2025. All rights reserved.")
        self.dev_name.setStyleSheet("color: white; font-size: 15px;")
        self.dev_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.dev_name)

if __name__ == "__main__":
    # For quick testing
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    splash = SplashWindow()
    splash.show()
    sys.exit(app.exec())
