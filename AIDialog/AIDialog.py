import json

from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QMessageBox
from backend_controller.db_handle_AI import save_chat_message,get_smart_suggestions


class AIDialog:
    def __init__(self, name, phone_number, user_id):
        self.name = name
        self.phone_number = phone_number
        self.user_id = user_id


    def show_suggestions_dialog(self, message_input):
        """Show AI-generated message suggestions and save them to the database."""
        user_message = message_input.text()


        if not user_message.strip():
            QMessageBox.warning(None, "Empty Input", "Please type a message to get suggestions!")
            return

        # Fetch AI suggestions
        suggestions = get_smart_suggestions(user_message)

        # Save suggestions to the database (as JSON)
        save_chat_message(self.user_id, user_message, json.dumps(suggestions))

        # Display suggestions in a dialog
        dialog = QDialog()
        dialog.setWindowTitle("AI Smart Suggestions")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")
        layout = QVBoxLayout(dialog)

        suggestion_list = QListWidget()
        for suggestion in suggestions:
            suggestion_list.addItem(suggestion)


        def on_item_clicked(item):
            """Set message_input text to the clicked suggestion."""
            message_input.setText(item.text())
            dialog.close()

        suggestion_list.itemClicked.connect(on_item_clicked)

        layout.addWidget(suggestion_list)
        dialog.exec_()



