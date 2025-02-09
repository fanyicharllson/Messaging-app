from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QMessageBox, QLabel, QHBoxLayout
from backend_controller.db_handler_socials import post_status, get_friend_and_user_statuses, like_status, get_users_who_liked_status, get_users_who_viewed_status, track_status_view, delete_status
import qtawesome as qta


class StatusDialog(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.status = None
        self.setFixedSize(600, 400)

    def show_post_status_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("Post Status")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QVBoxLayout()

        status_input = QTextEdit()
        status_input.setPlaceholderText("What's on your mind?")
        layout.addWidget(status_input)

        post_button = QPushButton("Post")
        post_button.setCursor(Qt.PointingHandCursor)
        post_button.setStyleSheet(
            """
            QPushButton {
                background-color: #1abc9c;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            """
        )
        layout.addWidget(post_button)



        post_button.clicked.connect(lambda: post_status(user_id=self.user_id, content=status_input.toPlainText()))

        dialog.setLayout(layout)
        dialog.exec()

    def show_friend_statuses_dialog(self):
        """
           Displays a dialog showing statuses from the user and their friends.
           Allows the user to delete their own statuses with a delete icon.
           """
        statuses = get_friend_and_user_statuses(self.user_id)

        if not statuses:
            QMessageBox.information(None, "No Statuses", "No statuses to display.")
            return

        dialog = QDialog()
        dialog.setWindowTitle("View Statuses")
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")
        layout = QVBoxLayout()

        for status in statuses:
            status_layout = QHBoxLayout()

            # Status content button
            button = QPushButton(f"{status['user']} ({status['timestamp']})")
            button.setStyleSheet(
                "background-color: #1abc9c; color: white; font-size: 16px; padding: 10px; border: none; border-radius: 5px;")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _, s=status: self.show_status_content_dialog(s))
            status_layout.addWidget(button)

            print(f"User ID: {self.user_id}, Status ID: {status['user_id']}")

            # Delete button with icon (only for the user's statuses)
            if status['user_id'] == self.user_id:  # Check if the status belongs to the current user
                delete_button = QPushButton()
                delete_button.setIcon(qta.icon('fa.trash', color='white'))  # Use a trash icon
                delete_button.setStyleSheet(
                    "background-color: #e74c3c; border: none; border-radius: 5px; padding: 10px;")
                delete_button.setCursor(Qt.PointingHandCursor)
                delete_button.clicked.connect(
                    lambda _, s=status: self.confirm_delete_status(s, dialog))  # Pass the status and dialog
                status_layout.addWidget(delete_button)

            layout.addLayout(status_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def show_status_content_dialog(self, status):
            """
            Displays the content of a friend's status in a dialog, along with likes and views.

            Args:
                status (dict): A dictionary containing status details.
            """
            dialog = QDialog()
            dialog.setWindowTitle(f"{status['user']}'s Status")
            dialog.setStyleSheet("background-color: #2c3e50; color: white; ")
            dialog.setFixedSize(600, 400)

            layout = QVBoxLayout()

            # Status content
            content_label = QLabel(f"Posted by: {status['user']}\n\n{status['content']}")
            content_label.setWordWrap(True)
            layout.addWidget(content_label)

            # Likes section
            likes_label = QLabel("Likes:")
            # like_button.clicked.connect(lambda: self.like_status(status['status_id'], self.user_id))
            layout.addWidget(likes_label)

            users_who_liked = get_users_who_liked_status(status['status_id'])
            for user in users_who_liked:
                layout.addWidget(QLabel(f"- {user}"))

            # Views section
            views_label = QLabel("Views:")
            layout.addWidget(views_label)

            users_who_viewed = get_users_who_viewed_status(status['status_id'])
            for user in users_who_viewed:
                layout.addWidget(QLabel(f"- {user}"))

            # Track view for the current user
            track_status_view(status['status_id'], self.user_id)

            like_button = QPushButton("Like")
            like_button.setStyleSheet(
                "background-color: #1abc9c; color: white; font-size: 16px; padding: 10px; border: none; border-radius: 5px;")
            like_button.setCursor(Qt.PointingHandCursor)
            like_button.clicked.connect(lambda: like_status(status['status_id'], self.user_id))
            layout.addWidget(like_button)

            dialog.setLayout(layout)
            dialog.exec()

    def confirm_delete_status(self, status, parent_dialog):
        """
        Shows a confirmation prompt to delete a status.
        """
        reply = QMessageBox.question(
            None,
            "Confirm Delete",
            f"Are you sure you want to delete this status?\n\n{status['content']}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            delete_status(status['user_id'], status['status_id'])  # Pass both user_id and status_id
            QMessageBox.information(None, "Status Deleted", "The status has been deleted.")
            parent_dialog.close()  # Close the dialog and refresh
            self.show_friend_statuses_dialog()  # Reopen the dialog with updated statuses
