import base64
import json

import qtawesome as qta
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QToolButton, QApplication, QInputDialog, QMessageBox,
    QFileDialog, QDialog
)
from PySide6.QtCore import Qt, QSize, QTimer
from auth_view import login_window #avoiding circular imports
from backend_controller import db_handler_friends
from helpers.log_message import LogMessage
from Status_view.Status_dialog import StatusDialog
from Create_Group_View.create_group import GroupDialog
from AIDialog.AIDialog import AIDialog
from backend_controller.db_handle_AI import analyze_sentiment,save_chat_message
from settings.SettingDialog import SettingDialog


class MainWindow(QMainWindow):
    chat_display: QTextEdit

    def __init__(self, name, phone_number, user_id):
        super().__init__()
        self.selected_friend = None
        self.message_poll_timer = None
        self.message_input = None
        self.login_window = None
        self.message = LogMessage()
        self.group = GroupDialog(user_id, phone_number)
        self.ai = AIDialog(name, phone_number, user_id)
        self.setting = SettingDialog(user_id, name, phone_number)
        self.status = StatusDialog(user_id)
        self.setWindowTitle("ChatHub")
        self.setFixedSize(1110, 660)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self.name = name
        self.phone_number = phone_number
        self.user_id = user_id

        # Start polling for new messages
        self.start_polling_for_messages()

        #invoke friend requests
        db_handler_friends.check_friend_requests(self.user_id)

        notifications = db_handler_friends.fetch_notifications(self.user_id, "notifications")
        message_notifications = db_handler_friends.fetch_notifications(self.user_id, "message_notifications")
        if notifications:
            self.message.show_success_message(
                f"Hey {self.name}! You have {len(notifications) + len(message_notifications)} new notifications. Click the bell icon to view them.")


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

        message_notifications = db_handler_friends.fetch_notifications(self.user_id, "message_notifications")
        if message_notifications:
            for _, message, created_at in message_notifications:
                self.message.show_success_message(f"{message} at {created_at}.")

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
            ("fa.eye", "View Status", self.handle_view_status_click),
            ("fa.user", "Profile", self.handle_profile_click),
            ("fa.group", "Create Group", self.handle_create_group_click),
            ("fa.comments", "Message Group", self.handle_message_group),
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
        icon_container.setFixedWidth(80)
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

        # fetch friends from the database
        friends = db_handler_friends.load_friends(self.user_id)
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

        # Load profile picture or placeholder
        profile_pic_path = db_handler_friends.get_profile_picture_path_from_db(self.user_id)
        profile_pic_label = QLabel()
        profile_pixmap = QPixmap(profile_pic_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic_label.setPixmap(profile_pixmap)
        profile_pic_label.setFixedSize(50, 50)
        profile_pic_label.setCursor(Qt.PointingHandCursor)
        profile_pic_label.setStyleSheet("border-radius: 25px; border: 2px solid #1abc9c;")
        profile_pic_label.mousePressEvent = self.handle_profile_click  # Open dialog on click

        #adding username label beside profile pic
        username_label = QLabel(self.name)
        username_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        chat_area.addWidget(username_label, alignment=Qt.AlignLeft)

        # Chat header
        chat_header = QLabel(f"Welcome {self.name}! Select a friend to start chatting!")
        chat_header.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

        chat_area.addWidget(profile_pic_label)
        chat_area.addWidget(chat_header, alignment=Qt.AlignLeft)

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

        # --- Smart Suggestions Button ---
        suggest_btn = QPushButton("Reply suggestions-AI")
        suggest_btn.setCursor(Qt.PointingHandCursor)
        suggest_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
            """
        )
        suggest_btn.clicked.connect(self.show_suggestions_dialog)  # New method
        input_layout.addWidget(suggest_btn)

        # --- New buttons for sending images and documents ---
        image_btn = QPushButton("Image")
        image_btn.setCursor(Qt.PointingHandCursor)
        image_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
            """
        )
        image_btn.clicked.connect(self.send_image)
        input_layout.addWidget(image_btn)

        doc_btn = QPushButton("Doc")
        doc_btn.setCursor(Qt.PointingHandCursor)
        doc_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #8e44ad;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
            """
        )
        doc_btn.clicked.connect(self.send_doc)
        input_layout.addWidget(doc_btn)
        # --- End new buttons ---

        chat_area.addLayout(input_layout)

        # Chat area container
        chat_area_container = QWidget()
        chat_area_container.setLayout(chat_area)
        return chat_area_container

    def start_polling_for_messages(self):
        """Starts a timer to poll for new messages."""
        self.message_poll_timer = QTimer()
        self.message_poll_timer.timeout.connect(self.check_for_new_messages)
        self.message_poll_timer.start(2000)  # Poll every 2 seconds

    def check_for_new_messages(self):
        """Checks for new messages from the database."""
        selected_friend = getattr(self, "selected_friend", None)

        print(f"selected friend: {selected_friend}")
        if not selected_friend:
            return

            # Append the latest message to the chat display (if not already shown)
        latest_message = db_handler_friends.check_for_new_messages(self.user_id, selected_friend["id"])

        if latest_message:
            sender_id, content, timestamp = latest_message
            sender = "You" if sender_id == self.user_id else "Friend"

            # Check if the message is already displayed
            last_message = self.chat_display.toPlainText().split("\n")[-1]
            if last_message != f"{sender} ({timestamp}): {content}":
                self.chat_display.append(f"{sender} ({timestamp}): {content}")



    def handle_status_click(self):
        """Opens a dialog to post a status."""
        self.status.show_post_status_dialog()

    def handle_profile_click(self, event):
        """Opens a dialog to edit profile details."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Profile")
        dialog.setFixedSize(600, 400)

        # Layout for the dialog
        layout = QVBoxLayout()

        # Display current profile picture
        current_pic_label = QLabel("Current Picture:")
        layout.addWidget(current_pic_label)
        current_profile_pic = QLabel()
        current_pixmap = QPixmap(db_handler_friends.get_profile_picture_path_from_db(self.user_id)).scaled(100, 100, Qt.KeepAspectRatio,
                                                                                 Qt.SmoothTransformation)
        current_profile_pic.setPixmap(current_pixmap)
        current_profile_pic.setFixedSize(100, 100)
        current_profile_pic.setStyleSheet("border-radius: 50px; border: 2px solid #1abc9c;")
        layout.addWidget(current_profile_pic, alignment=Qt.AlignCenter)

        # Button to upload a new picture
        upload_button = QPushButton("Upload New Picture")
        upload_button.setStyleSheet(
            "background-color: #1abc9c; color: white; font-size: 16px; padding: 10px; border: none; border-radius: 5px;")
        upload_button.setCursor(Qt.PointingHandCursor)
        upload_button.clicked.connect(self.upload_new_profile_picture)
        layout.addWidget(upload_button, alignment=Qt.AlignCenter)

        # Name input
        name_label = QLabel("Name:")
        name_input = QLineEdit(self.name)
        name_input.setStyleSheet(
            "font-size: 16px; padding: 10px; border: 1px solid #1abc9c; border-radius: 5px;")
        layout.addWidget(name_label)
        layout.addWidget(name_input)

        # Number input
        number_label = QLabel("Phone Number:")
        number_input = QLineEdit(self.phone_number)
        number_input.setStyleSheet(
            "font-size: 16px; padding: 10px; border: 1px solid #1abc9c; border-radius: 5px;")
        layout.addWidget(number_label)
        layout.addWidget(number_input)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: db_handler_friends.save_profile_changes(dialog, self.user_id, name_input.text(), number_input.text()))
        save_button.setStyleSheet(
            "background-color: #1abc9c; color: white; font-size: 16px; padding: 10px; border: none; border-radius: 5px;")
        save_button.setCursor(Qt.PointingHandCursor)
        self.name = name_input.text()
        self.phone_number = number_input.text()
        layout.addWidget(save_button, alignment=Qt.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()

    def upload_new_profile_picture(self):
        """Uploads a new profile picture and updates the database."""
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        if image_path:
            # Update the profile picture in the database
            db_handler_friends.update_profile_picture_in_db( self.user_id, image_path)

    def handle_create_group_click(self):
        """Handles group creation"""
        self.group.handle_create_group()

    def handle_message_group(self):
        """Show group messages"""
        self.group.handle_message_group()

    def handle_notification_click(self):
        """Display notifications for the user."""
        self.chat_display.clear()

        message_notifications = db_handler_friends.fetch_notifications(self.user_id, "message_notifications")
        if message_notifications:
            for _, message, created_at in message_notifications:
                self.chat_display.append(f"[{created_at}]: {message}")
            db_handler_friends.mark_notifications_as_read(self.user_id, "message_notifications")

        notifications = db_handler_friends.fetch_notifications(self.user_id, "notifications")
        if notifications:
            for notification_id, message, created_at in notifications:
                self.chat_display.append(f"[{created_at}]: {message}")
            db_handler_friends.mark_notifications_as_read(self.user_id, "notifications")
        else:
            self.message.show_error_message("No new notifications.")


    def handle_add_friend_click(self):
        """Send a friend request to another user."""
        # Create a custom QInputDialog
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle("Add Friend")
        input_dialog.setLabelText("Enter the name of your friend:")
        input_dialog.setInputMode(QInputDialog.TextInput)
        input_dialog.setTextValue("")  # Default value
        input_dialog.resize(600, 500)  # Increase size
        input_dialog.setStyleSheet("""
            QInputDialog {
                background-color: #2c3e50;
                border: 1px solid white;
                border-radius: 8px;
            }
            QLabel {
                font-size: 16px;
                color: white;
            }
            QLineEdit {
                font-size: 15px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 14px;
                color: white;
                background-color: #1abc9c;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)

        # Set the font for the label and text input
        font = QFont("Arial", 12)
        input_dialog.setFont(font)

        # Show the dialog and get the result
        if input_dialog.exec_() == QInputDialog.Accepted:
            friend_name = input_dialog.textValue()

            if not friend_name:
                QMessageBox.warning(self, "Warning", "Please enter a friend name.")
                return

            else:
                # Normalize the friend name to prevent input issues
                friend_name = friend_name.strip().title()


                # Call the add_friend_request function
                try:
                    result = db_handler_friends.add_friend_request(self.user_id, friend_name)
                    if not result:
                        return
                    QMessageBox.information(self, "Success", f"Friend request sent to {friend_name}!")
                except Exception as e:
                    # Handle any unexpected errors and show feedback
                    QMessageBox.critical(self, "Error", f"Failed to send friend request: {str(e)}")

    def handle_remove_friend_click(self):
        """ Remove a friend from the friends list."""
        QMessageBox.information(self, "Information", "This feature is currently unavailable.")

    def handle_settings_click(self):
        """Redirects to the settings page."""
        self.setting.open_settings_dialog()

    def handle_logout_click(self):
        """Handle logout button click."""
        self.open_login_window()

    def open_chat_with_friend(self, item):
        """Handle opening a chat with a selected friend."""
        self.chat_display.clear()
        self.chat_display.append(f"Chatting with {item.text()}...\n")
        self.chat_display.setFocus()

        # Get friend name from the item text
        friend_name = item.text()


        # Load friends data (should be a list of tuples like [(friend_name, friend_id), ...])
        friends = db_handler_friends.load_friends(self.user_id)

        # Use a generator expression to find the tuple matching the selected friend name
        friend_data = next((friend for friend in friends if friend[0] == friend_name), None)

        if not friend_data:
            QMessageBox.warning(self, "Warning", f"Could not find details for {friend_name}.")
            return

        # Now, friend_data is expected to be a tuple like (friend_name, friend_id)
        self.selected_friend = {
            "id": friend_data[1],  # Friend's numeric ID
            "name": friend_name,
        }

        # Load chat history with the selected friend
        self.load_chat_history(friend_data[1])

    def send_message(self):
        """Handles sending messages."""
        selected_friend = getattr(self, "selected_friend", None)
        message_content = self.message_input.text().strip()

        # print(f"selected friend from send_message {selected_friend}")

        if not selected_friend:
            QMessageBox.warning(self, "Warning", "Please select a friend to chat with.")
            return

        if not message_content:
            QMessageBox.warning(self, "Warning", "Cannot send an empty message.")
            return

        # Save the message to the database
        db_handler_friends.save_message(self.user_id, selected_friend["id"], message_content)

        # Clear the message input field
        self.message_input.clear()

        # Refresh the chat display for both sender and receiver
        self.load_chat_history(selected_friend["id"])

        QMessageBox.information(self, "Success", f"Message sent to {selected_friend['name']}!")



    def load_chat_history(self, friend_id):
        """Loads the chat history between the current user and the selected friend."""

        chat_history = db_handler_friends.load_chat_history_db(self.user_id, friend_id)

        # Clear the chat display and load the conversation
        self.chat_display.clear()
        for sender_id, content, timestamp, message_type in chat_history:
            # If the message is a file (image or doc), process the content as JSON.
            if message_type == "image":
                try:
                    file_info = json.loads(content)
                    image_data = base64.b64decode(file_info["data"])
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                    self.chat_display.append(f"{sender_id} ({timestamp}):")
                    self.chat_display.layout().addWidget(image_label)
                except Exception as e:
                    self.chat_display.append(f"[IMAGE]: (Error loading image)")
                    print(f"Error displaying image: {str(e)}")

            elif message_type == "doc":
                try:
                    file_info = json.loads(content)
                    file_name = file_info["file_name"]
                    self.chat_display.append(f"[DOCUMENT]: {file_name} (Click to download)")
                    # Optionally add a button for saving the document
                except Exception as e:
                    self.chat_display.append(f"[DOCUMENT]: (Error loading document)")
                    print(f"Error displaying document: {str(e)}")
            else:
             sender = "You" if sender_id == self.user_id else "Friend"
             self.chat_display.append(f"{sender} ({timestamp}): {content}")


    def open_login_window(self):
        # Create and show the login window if not already created
        if self.login_window is None:
            self.login_window = login_window.LoginWindow()

        self.login_window.show()
        self.close()

    def send_image(self):
        """Handles sending image files."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    file_data = file.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the image: {str(e)}")
                return

            selected_friend = getattr(self, "selected_friend", None)
            if not selected_friend:
                QMessageBox.warning(self, "Warning", "Please select a friend to chat with.")
                return

            # Save the image file as a message to the database.
            # You need to implement save_file_message() in your db_handler_friends module.
            db_handler_friends.save_file_message(
                sender_id=self.user_id,
                receiver_id=selected_friend["id"],
                file_data=file_data,
                file_type="image",
                file_name=file_path.split("/")[-1]
            )
            self.load_chat_history(selected_friend["id"])

    def send_doc(self):
        """Handles sending document files."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "", "Documents (*.pdf *.doc *.docx *.txt)"
        )
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    file_data = file.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the document: {str(e)}")
                return

            selected_friend = getattr(self, "selected_friend", None)
            if not selected_friend:
                QMessageBox.warning(self, "Warning", "Please select a friend to chat with.")
                return

            # Save the document file as a message to the database.
            db_handler_friends.save_file_message(
                sender_id=self.user_id,
                receiver_id=selected_friend["id"],
                file_data=file_data,
                file_type="document",
                file_name=file_path.split("/")[-1]
            )
            self.load_chat_history(selected_friend["id"])


    def handle_view_status_click(self):
        """Handle view status button click."""
        self.status.show_friend_statuses_dialog()

    def show_suggestions_dialog(self):
        """Show AI suggestion dialog"""
        self.ai.show_suggestions_dialog(self.message_input)

    def send_message_with_emojis(self):
        """Send a message with AI-generated emojis and save it to the database."""
        user_message = self.message_input.text()
        if not user_message.strip():
            return

        # Analyze sentiment and add emojis
        emojis = analyze_sentiment(user_message)
        full_message = f"{user_message} {emojis}"
        self.chat_display.append(f"You: {full_message}")

        # Save message to the database
        save_chat_message(self.user_id, full_message, None)  # No suggestions here

        self.message_input.clear()

