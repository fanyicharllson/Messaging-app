import qtawesome as qta
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QToolButton, QApplication, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from auth_view import login_window #avoiding circular imports
from backend_controller import db_handler_friends
from helpers.log_message import LogMessage


class MainWindow(QMainWindow):
    chat_display: QTextEdit

    def __init__(self, name, phone_number, user_id):
        super().__init__()
        self.message_input = None
        self.login_window = None
        self.message = LogMessage()
        self.setWindowTitle("ChatHub")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self.name = name
        self.phone_number = phone_number
        self.user_id = user_id

        #invoke notifications
        db_handler_friends.check_friend_requests(self.user_id)

        notifications = db_handler_friends.fetch_notifications(self.user_id)
        if notifications:
            self.message.show_success_message(
                f"Hey {self.name}! You have {len(notifications)} new notifications. Click the bell icon to view them.")


        # Apply tooltip style globally
        QApplication.instance().setStyleSheet("""
                   QToolTip {
                       color: white;
                       background-color: #34495e;
                       border: 1px solid #1abc9c;
                       font-size: 14px;
                       padding: 5px;
                       border-radius: 5px;
                   }
               """)

        # Main layout
        main_layout = QHBoxLayout()

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, stretch=1)

        # Chat Area
        self.chat_area = self.create_chat_area()
        main_layout.addWidget(self.chat_area, stretch=3)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_sidebar(self):
        """Creates the left sidebar with icons and friend list split horizontally."""
        sidebar = QHBoxLayout()  # Use HBox to align icon and friend list horizontally
        sidebar.setContentsMargins(10, 10, 10, 10)
        sidebar.setSpacing(15)

        # Left section for icons
        icon_layout = QVBoxLayout()
        icons = [
            ("fa.bell", "Notification", self.handle_notification_click),
            ("fa.circle", "Status", self.handle_status_click),
            ("fa.user", "Profile", self.handle_profile_click),
            ("fa.group", "Create Group", self.handle_create_group_click),
            ("fa.plus-circle", "Add Friend", self.handle_add_friend_click),
            ("fa.minus-circle", "Remove Friend", self.handle_remove_friend_click),
            ("fa.cog", "Settings", self.handle_settings_click),
            ("fa.sign-out", "Logout", self.handle_logout_click),
        ]
        for icon_name, tooltip, handler in icons:
            btn = QToolButton()
            btn.setIcon(qta.icon(icon_name, color="#1abc9c"))
            btn.setIconSize(QSize(30, 30))
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                """
                QToolButton {
                    background: none;
                    border: none;
                    margin: 10px;
                    color: #1abc9c;
                }
                QToolButton:hover {
                    background-color: #34495e;
                    border-radius: 10px;
                }
                """
            )
            btn.clicked.connect(handler)
            icon_layout.addWidget(btn, alignment=Qt.AlignHCenter)

        # Left section container for icons
        icon_container = QWidget()
        icon_container.setLayout(icon_layout)
        icon_container.setFixedWidth(60)
        sidebar.addWidget(icon_container)

        # Separator line between icons and friend list (optional)
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: #34495e;")
        sidebar.addWidget(separator)

        # Right section for friend list
        friend_list = QListWidget()
        friend_list.setStyleSheet(
            """
            QListWidget {
                background-color: #34495e;
                border: none;
                color: white;
                font-size: 16px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #1abc9c;
            }
            QListWidget::item:selected {
                background-color: #16a085;
                color: white;
            }
            """
        )

        # Add some dummy friends
        friends = db_handler_friends.load_friends(self.user_id)
        print(f"friends are: {friends}")
        print(f"id is: {self.user_id}")
        for friend in friends:
            item = QListWidgetItem(friend[0])
            friend_list.addItem(item)

        if not friends:
            no_friends_item = QListWidgetItem("No friends found. \nClick '+' to add friends.")
            no_friends_item.setFlags(no_friends_item.flags() & ~Qt.ItemIsSelectable)
            friend_list.addItem(no_friends_item)

        friend_list.itemClicked.connect(self.open_chat_with_friend)

        # Right section container for friend list
        friend_list_container = QWidget()
        friend_list_layout = QVBoxLayout()
        friend_list_layout.addWidget(friend_list)
        friend_list_layout.setContentsMargins(0, 0, 0, 0)
        friend_list_layout.setSpacing(0)
        friend_list_container.setLayout(friend_list_layout)
        sidebar.addWidget(friend_list_container, stretch=1)

        # Sidebar container
        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar)
        sidebar_container.setFixedWidth(300)  # Adjust the overall width
        return sidebar_container

    def create_chat_area(self):
        """Creates the chat area where conversations happen."""
        chat_area = QVBoxLayout()
        chat_area.setContentsMargins(10, 10, 10, 10)
        chat_area.setSpacing(15)



        # Chat header
        chat_header = QLabel(f"Welcome {self.name}! Select a friend to start chatting!")
        chat_header.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        chat_area.addWidget(chat_header, alignment=Qt.AlignCenter)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #34495e;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: 1px solid #1abc9c;
                border-radius: 5px;
            }
            """
        )
        chat_area.addWidget(self.chat_display)

        # Message input and send button
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #34495e;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: 1px solid #1abc9c;
                border-radius: 5px;
            }
            """
        )
        input_layout.addWidget(self.message_input)

        send_btn = QPushButton("Send")
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet(
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
            QPushButton:pressed {
                background-color: #149174;
            }
            """
        )
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        chat_area.addLayout(input_layout)

        # Chat area container
        chat_area_container = QWidget()
        chat_area_container.setLayout(chat_area)
        return chat_area_container

    def handle_status_click(self):
        self.chat_display.append("Status button clicked!")
        # Add specific logic for Status here

    def handle_profile_click(self):
        self.chat_display.append("Profile button clicked!")
        # Add specific logic for Profile here

    def handle_create_group_click(self):
        self.chat_display.append("Create Group button clicked!")
        # Add specific logic for creating a group here

    def handle_notification_click(self):
        """Display notifications for the user."""
        self.chat_display.clear()

        notifications = db_handler_friends.fetch_notifications(self.user_id)
        if notifications:
            self.message.show_success_message(f"Hey {self.name}! You have {len(notifications)} new notifications. Click the bell icon to view them.")
            for notification_id, message, created_at in notifications:
                self.chat_display.append(f"[{created_at}]: {message}")
            db_handler_friends.mark_notifications_as_read(self.user_id)
        else:
            self.chat_display.append("No new notifications.")

    def handle_add_friend_click(self):
        """Send a friend request to another user."""
        # Get friend name input from the user
        friend_name, ok = QInputDialog.getText(
            self, "Add Friend", "Enter the name of your friend:"
        )

        if ok and friend_name:
            # Normalize the friend name to prevent input issues
            friend_name = friend_name.strip().title()

            # Call the add_friend_request function
            try:
                db_handler_friends.add_friend_request(self.user_id, friend_name)
                # Only update the chat display if the request was successful
                self.chat_display.append(f"Friend request sent to {friend_name}")
            except Exception as e:
                # Handle any unexpected errors and show feedback
                QMessageBox.critical(self, "Error", f"Failed to send friend request: {str(e)}")

    def handle_remove_friend_click(self):
        self.chat_display.append("Remove Friend button clicked!")
        # Add specific logic for removing a friend here

    def handle_settings_click(self):
        self.chat_display.append("Settings button clicked!")
        # Add specific logic for settings here

    def handle_logout_click(self):
        """Handle logout button click."""
        self.open_login_window()

    def open_chat_with_friend(self, item):
        """Handle opening a chat with a selected friend."""
        self.chat_display.clear()
        self.chat_display.append(f"Chatting with {item.text()}...\n")
        self.chat_display.setFocus()

    def send_message(self):
        """Handle sending a message."""
        message = self.message_input.text().strip()
        if message:
            self.chat_display.append(f"You: {message}")
            self.message_input.clear()

    def open_login_window(self):
        # Create and show the login window if not already created
        if self.login_window is None:
            self.login_window = login_window.LoginWindow()

        self.login_window.show()
        self.close()
