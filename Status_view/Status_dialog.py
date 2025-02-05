from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QMessageBox, QLabel
from backend_controller.db_handler_socials import post_status, get_friend_and_user_statuses, like_status, get_users_who_liked_status, get_users_who_viewed_status, track_status_view


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
            button = QPushButton(f"{status['user']} ({status['timestamp']})")
            button.setStyleSheet("background-color: #1abc9c; color: white; font-size: 16px; padding: 10px; border: none; border-radius: 5px;")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _, s=status: self.show_status_content_dialog(s))
            layout.addWidget(button)



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
            dialog.setStyleSheet("background-color: #2c3e50; color: white;")
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
