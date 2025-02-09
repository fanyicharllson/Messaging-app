from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QMessageBox, QCheckBox, QPushButton, QLabel, \
    QTextEdit, QWidget, QInputDialog, QHBoxLayout
from backend_controller import db_handler_friends, db_handler, db_handler_groups



class GroupDialog:
    def __init__(self, user_id, phone_number):
        self.user_id  = user_id
        self.phone_number = phone_number

    def handle_create_group(self):
        """Handles group creation."""
        dialog = QDialog()
        dialog.setWindowTitle("Create Group")
        dialog.resize(400, 300)
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")

        # Layouts
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()
        friends_layout = QVBoxLayout()

        # Widgets
        group_name_input = QLineEdit()
        group_name_input.setStyleSheet(
            "font-size: 16px; padding: 10px; border: 1px solid #1abc9c; border-radius: 5px;")
        group_name_input.setPlaceholderText("Enter group name")
        friend_checkboxes = []

        # Fetch friends from the database
        friends = db_handler_friends.load_friends(self.user_id)
        if not friends:
            QMessageBox.warning(None, "No Friends", "You don't have any friends to add to the group.")
            return

        # Create checkboxes for friends
        for friend_name, friend_id in friends:
            checkbox = QCheckBox(friend_name)
            checkbox.setProperty("friend_id", friend_id)  # Store friend ID
            friend_checkboxes.append(checkbox)
            friends_layout.addWidget(checkbox)

        # Buttons
        add_group_button = QPushButton("Add Group")
        cancel_button = QPushButton("Cancel")

        add_group_button.setCursor(Qt.PointingHandCursor)
        add_group_button.setStyleSheet(
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
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet(
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

        # Layout assembly
        form_layout.addRow("Group Name:", group_name_input)
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Select Friends:"))
        layout.addLayout(friends_layout)
        layout.addWidget(add_group_button)
        layout.addWidget(cancel_button)

        # Button handlers
        add_group_button.clicked.connect(
            lambda: self.add_group_to_db(dialog, group_name_input.text(), friend_checkboxes))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def add_group_to_db(self, dialog, group_name, friend_checkboxes):
        """Adds a group to the database."""
        group_name = group_name.strip()
        selected_friends = [cb.property("friend_id") for cb in friend_checkboxes if cb.isChecked()]

        if not group_name:
            QMessageBox.warning(None, "Invalid Input", "Group name cannot be empty!")
            return

        if not selected_friends:
            QMessageBox.warning(None, "No Friends Selected", "Please select at least one friend to add to the group.")
            return

        # store groups to db
        db_handler_groups.add_group(dialog, self.user_id, selected_friends, group_name)

    def handle_message_group(self):
        """Handles messaging a group."""
        groups = db_handler_groups.fetch_groups_for_user(self.user_id)  # Fetch groups created by the user

        if not groups:
            QMessageBox.warning(None, "No Groups",
                                "You are not part of any groups. Please create or join a group first.")
            return
        # Create a dialog to show groups
        dialog = QDialog()
        dialog.setWindowTitle("Message Group")
        dialog.resize(600, 400)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QVBoxLayout(dialog)

        for group_id, group_name in groups:
            # Fetch group members for the current group
            members = db_handler_groups.fetch_group_members(group_id)
            member_names = ", ".join([member[1] for member in members])  # Concatenate member names

            # Create a widget for the group name and members
            group_widget = QWidget()
            group_layout = QVBoxLayout(group_widget)

            #get admin name
            # name = db_handler_groups.get_group_creator(group_id)


            # Get admin name and check if the current user is the admin
            creator_id, creator_name = db_handler_groups.get_group_creator(group_id)
            is_admin = self.user_id == creator_id

            group_label = QLabel(f"Group Name: {group_name} -------> Admin: {creator_name}")
            group_label.setStyleSheet("font-size: 16px;")
            group_layout.addWidget(group_label)

            members_label = QLabel(f"Members: {member_names}")
            members_label.setStyleSheet("font-size: 14px; color: #bdc3c7;")
            group_layout.addWidget(members_label)

            # Add a button to open the group chat
            button = QPushButton("Open Chat")
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
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
            button.setProperty("group_id", group_id)  # Store group ID
            button.clicked.connect(lambda _, gid=group_id: self.open_group_chat(dialog, gid))
            group_layout.addWidget(button)

            # Add a button to add members (only for admin)
            add_member_button = QPushButton("Add Member")
            add_member_button.setCursor(Qt.PointingHandCursor)
            add_member_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                """
            )
            if is_admin:
                add_member_button.clicked.connect(lambda _, gid=group_id: self.show_add_members_dialog(gid))
            else:
                add_member_button.clicked.connect(
                    lambda: QMessageBox.warning(None, "Permission Denied", "Only the group admin can add members.")
                )
            group_layout.addWidget(add_member_button)

            layout.addWidget(group_widget)

        dialog.exec_()

    def show_add_members_dialog(self, group_id):
        """Shows a dialog for the admin to add friends to the group."""

        # Fetch current group members to exclude them from the selection
        current_members = db_handler_groups.fetch_group_members(group_id)
        current_member_ids = {member[0] for member in current_members}  # Extract member IDs

        # Fetch user's friends
        available_friends = db_handler_groups.load_friends(self.user_id)
        filtered_friends = [(friend_id, friend_name) for friend_id, friend_name in available_friends if
                            friend_id not in current_member_ids]

        if not available_friends:
            QMessageBox.information(None, "No Friends Available", "All your friends are already in the group!")
            return

        # Create the dialog
        dialog = QDialog()
        dialog.setWindowTitle("Add Members to Group")
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")
        dialog.resize(600, 400)
        layout = QVBoxLayout(dialog)

        title = QLabel("Select friends to add to the group:")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ecf0f1;")
        layout.addWidget(title)

        checkboxes = []
        for friend_id, friend_name in filtered_friends:
            print(f"Friend ID: {friend_id}, Friend Name: {friend_name}, Type: {type(friend_name)}")
            checkbox = QCheckBox(friend_name)  # Show friend's name
            checkbox.setProperty("friend_id", friend_id)  # Store the friend's ID
            checkbox.setStyleSheet("font-size: 14px; color: #bdc3c7;")
            checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # Add confirm and cancel buttons
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("Add Members")
        confirm_button.setStyleSheet(
            "background-color: #1abc9c; color: white; padding: 10px; border: none; border-radius: 5px;"
        )
        confirm_button.setCursor(Qt.PointingHandCursor)
        confirm_button.clicked.connect(lambda: self.add_members_to_group(dialog, group_id, checkboxes))
        button_layout.addWidget(confirm_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px; border: none; border-radius: 5px;"
        )
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        dialog.exec_()

    @staticmethod
    def add_members_to_group(dialog, group_id, checkboxes):
        """Adds the selected friends to the group."""
        selected_friend_ids = [
            checkbox.property("friend_id") for checkbox in checkboxes if checkbox.isChecked()
        ]

        if not selected_friend_ids:
            QMessageBox.warning(None, "No Selection", "Please select at least one friend to add.")
            return

        try:
            # Add each selected friend to the group
            for friend_id in selected_friend_ids:
                db_handler_groups.add_group_member(group_id, friend_id)

            QMessageBox.information(None, "Success", "Selected members were added successfully!")
            dialog.accept()  # Close the dialog after successful addition

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add members: {e}")
            print(f"Failed to add members: {e}")

    def open_group_chat(self, parent_dialog, group_id):
        """Opens the group chat dialog."""
        parent_dialog.accept()  # Close the parent dialog

        dialog = QDialog()
        dialog.setWindowTitle("Group Chat")
        dialog.resize(400, 400)
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QVBoxLayout(dialog)

        # Display group messages
        message_area = QTextEdit()
        message_area.setReadOnly(True)
        layout.addWidget(message_area)

        message_area.clear()

        # fetch group message
        messages = db_handler_groups.fetch_group_message(group_id)




        if not messages:
            print(f"No message for create_group.py line 202")
            # QMessageBox.information(None, "Me", "Couldn't get group message")

        message_area.clear()
        for sender_name, content, timestamp in messages:

            message_area.append(f"[{timestamp}] {sender_name}: {content}")

        # Message input
        message_input = QLineEdit()
        message_input.setStyleSheet(
            "font-size: 16px; padding: 10px; border: 1px solid #1abc9c; border-radius: 5px;")
        message_input.setPlaceholderText("Type your message here...")
        layout.addWidget(message_input)

        send_button = QPushButton("Send")
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.setStyleSheet(
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
        send_button.clicked.connect(lambda: self.send_group_message(dialog, group_id, message_input, message_area))
        layout.addWidget(send_button)

        dialog.exec_()

    def send_group_message(self, dialog, group_id, message_input, message_area):
        """Sends a message to the group."""
        content = message_input.text().strip()
        if not content:
            QMessageBox.information(None, "No Content", "Cannot send empty message!")
            return

        result = db_handler_groups.store_group_message(self.user_id, group_id, content)
        message_input.clear()
        if result:
            QMessageBox.information(None, "Sent Message", "Message sent")
        else:
            QMessageBox.critical(None, "Sent not Message", "Message not sent")
            return

        # Display the new message
        message_area.append(f"[{QDateTime.currentDateTime().toString()}] You: {content}")
        message_input.clear()
