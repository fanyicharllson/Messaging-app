import qtawesome as qta
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QToolButton, QApplication
)
from PySide6.QtCore import Qt, QSize


class MainWindow(QMainWindow):
    chat_display: QTextEdit

    def __init__(self, name, phone_number):
        super().__init__()
        self.message_input = None
        self.setWindowTitle("ChatHub")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self.name = name
        self.phone_number = phone_number


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
            ("fa.circle", "Status"),
            ("fa.user", "Profile"),
            ("fa.group", "Create Group"),
            ("fa.plus-circle", "Add Friend"),
            ("fa.minus-circle", "Remove Friend"),
            ("fa.sign-out", "Logout"),
            ("fa.cog", "Settings"),
        ]
        for icon_name, tooltip in icons:
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
        friends = ["Alice", "Bob", "Charlie", "David", "Eve"]
        for friend in friends:
            item = QListWidgetItem(friend)
            friend_list.addItem(item)

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

    def open_chat_with_friend(self, item):
        """Handle opening a chat with a selected friend."""
        self.chat_display.append(f"Chatting with {item.text()}...\n")
        self.chat_display.setFocus()

    def send_message(self):
        """Handle sending a message."""
        message = self.message_input.text().strip()
        if message:
            self.chat_display.append(f"You: {message}")
            self.message_input.clear()
