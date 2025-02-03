from PySide6.QtWidgets import QMessageBox


class LogMessage:
    def __init__(self, parent=None):
        self.parent = parent

    def show_error_message(self, message):
        """Display an error message in a message box."""
        error_msg = QMessageBox(self.parent)
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setText(message)
        error_msg.setWindowTitle("Error")
        error_msg.exec()

    def show_success_message(self, message):
        """Display a success message in a message box."""
        success_msg = QMessageBox(self.parent)
        success_msg.setIcon(QMessageBox.Information)
        success_msg.setText(message)
        success_msg.setWindowTitle("Success")
        success_msg.exec()

    def clear_inputs(self, name_input, phone_input):
        """Clear input fields."""
        name_input.setPlaceholderText("Enter your phone number")
        phone_input.setPlaceholderText("Enter your name")