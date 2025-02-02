# main.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from chat_view.chat_window import ChatWindow
from welcome_view.loading_window import LoadingWindow
from welcome_view.splash_window import SplashWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create instances of the windows
    loading_window = LoadingWindow()
    splash_window = SplashWindow()
    chat_window = ChatWindow()

    # Show the loading window first
    loading_window.show()

    # After a set amount of time (e.g., 3000 milliseconds), hide the loading window and show the splash window.
    QTimer.singleShot(3000, lambda: (loading_window.close(), splash_window.show()))

    # Connect the splash window's continue signal to hide the splash and show the chat window.
    splash_window.continueClicked.connect(lambda: (splash_window.close(), chat_window.show()))

    sys.exit(app.exec())
