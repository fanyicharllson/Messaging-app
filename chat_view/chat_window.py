# chat_window.py
from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messaging App - ChatHub")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #ecf0f1;")

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # A header for the chat window
        header = QLabel("Chat Window")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin: 20px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # A text edit as a placeholder for chat content
        chat_area = QTextEdit()
        chat_area.setPlaceholderText("Chat messages will appear here...")
        chat_area.setStyleSheet("font-size: 16px;")
        layout.addWidget(chat_area)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    # For quick testing of the chat window
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    chat = ChatWindow()
    chat.show()
    sys.exit(app.exec())
