from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel, QLineEdit, QTextEdit
from backend_controller.db_handler import insert_feedback

class SettingDialog:
    def __init__(self, user_id, name, phone_number):
        self.user_id = user_id
        self.name = name
        self.phone_number = phone_number

    def open_settings_dialog(self):
        """
        Opens the Settings dialog for the messaging app.
        """
        dialog = QDialog()
        dialog.setWindowTitle("Settings")
        dialog.setMinimumSize(400, 300)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")
        layout = QVBoxLayout(dialog)

        # Buttons for settings categories
        account_button = QPushButton("Account Settings")
        account_button.setCursor(Qt.PointingHandCursor)
        account_button.setStyleSheet("background-color: #1abc9c; color: white; padding: 10px; border-radius: 5px;")
        account_button.clicked.connect(self.open_account_settings)

        privacy_button = QPushButton("Privacy & Security")
        privacy_button.setCursor(Qt.PointingHandCursor)
        privacy_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px;")
        privacy_button.clicked.connect(self.open_privacy_settings)

        about_button = QPushButton("About ChatHub")
        about_button.setCursor(Qt.PointingHandCursor)
        about_button.setStyleSheet("background-color: #9b59b6; color: white; padding: 10px; border-radius: 5px;")
        about_button.clicked.connect(self.open_about_dialog)

        # Add buttons to layout
        for button in [account_button, privacy_button, about_button]:
            layout.addWidget(button)

        dialog.setLayout(layout)
        dialog.exec()

    @staticmethod
    def open_account_settings():
        """Prompt the user to click the profile icon or image to edit their profile details."""
        QMessageBox.information(None, "Account Settings", "Click the profile icon(4th icon) or picture to edit your profile details.")

    @staticmethod
    def open_privacy_settings():
        """Handle privacy and security settings."""
        QMessageBox.information(None, "Privacy Settings",
                                "This feature will be implemented soon. Please try again later.")

    def open_about_dialog(self):
        """
        Opens the About ChatHub dialog.
        """
        dialog = QDialog()
        dialog.setWindowTitle("About ChatHub")
        dialog.setMinimumSize(400, 300)
        dialog.setStyleSheet("background-color: #34495e; color: white;")

        layout = QVBoxLayout(dialog)

        # Add "About ChatHub" section
        about_label = QLabel(
            "ChatHub\n\n"
            "ChatHub is a simple messaging app designed for seamless communication. "
            "Built with PySide and SQLite3, it's efficient, lightweight, and user-friendly.\n\n"
            "Creator: FANYI CHARLLSON\n"
            "Career: Software Engineer\n"
            "Contact: fanyicharlson@gmail.com\n"
            "Version: 1.0.0"
        )
        about_label.setStyleSheet("font-size: 14px; padding: 10px;")
        about_label.setWordWrap(True)
        layout.addWidget(about_label)

        # Add a button for feedback
        feedback_button = QPushButton("Send Feedback")
        feedback_button.setCursor(Qt.PointingHandCursor)
        feedback_button.setStyleSheet("background-color: #1abc9c; color: white; padding: 10px; border-radius: 5px;")
        feedback_button.clicked.connect(self.open_feedback_form)
        layout.addWidget(feedback_button)

        dialog.setLayout(layout)
        dialog.exec()

    def open_feedback_form(self):
        """
        Opens the feedback form dialog where users can submit their feedback.
        """
        dialog = QDialog()
        dialog.setWindowTitle("Send Feedback")
        dialog.setMinimumSize(400, 300)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QVBoxLayout(dialog)

        # Name field
        name_label = QLabel("Your Name:")
        name_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(name_label)

        name_edit = QLineEdit()
        name_edit.setText(self.name)  # Pre-fill with the user's default name
        name_edit.setStyleSheet("padding: 5px; font-size: 14px; border-radius: 5px;")
        layout.addWidget(name_edit)

        # Feedback field
        feedback_label = QLabel("Your Feedback:")
        feedback_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(feedback_label)

        feedback_edit = QTextEdit()
        feedback_edit.setStyleSheet("padding: 5px; font-size: 14px; border-radius: 5px;")
        layout.addWidget(feedback_edit)

        # Submit button
        submit_button = QPushButton("Submit Feedback")
        submit_button.setCursor(Qt.PointingHandCursor)
        submit_button.setStyleSheet("background-color: #1abc9c; color: white; padding: 10px; border-radius: 5px;")
        submit_button.clicked.connect(
            lambda: self.submit_feedback(name_edit.text(), feedback_edit.toPlainText(), dialog))
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        dialog.exec()

    @staticmethod
    def submit_feedback(name, feedback, dialog):
        """
        Handles feedback submission.
        """
        if not feedback.strip():
            QMessageBox.warning(None, "Incomplete", "Please provide feedback before submitting.")
            return

        # Insert feedback into the database
        insert_feedback(name, feedback)


        QMessageBox.information(None, f"Thank You {name}!", "Your feedback has been received.")
        dialog.close()

