import base64
import json
import sqlite3
import backend_controller.db_handler as db_handler
from PySide6.QtWidgets import QMessageBox




def connect_to_database():
    """
    Connect to the SQLite database and return the connection object.

    Returns:
        sqlite3.Connection: Connection object for the database.
    """
    conn = db_handler.create_connection()
    return conn

def close_database_connection(conn):
    """
    Close the database connection.

    Args:
        conn (sqlite3.Connection): Connection object for the database.
    """
    conn.close()

def add_friend_request(sender_id, friend_name, self=None):
    """Send a friend request."""
    print(f"Sender id from db_handler_friends.py {sender_id}")
    connection = connect_to_database()
    connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
    cursor = connection.cursor()

    # Normalize input
    friend_name = friend_name.strip().title()

    # Check if the entered friend exists in the database
    query = "SELECT id FROM users WHERE name = ?"
    cursor.execute(query, (friend_name,))
    result = cursor.fetchone()

    if result:
        receiver_id = result[0]

        # Check if the users are already friends
        cursor.execute(
            """
            SELECT id FROM friends
            WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)
            """,
            (sender_id, receiver_id, receiver_id, sender_id),
        )
        existing_friendship = cursor.fetchone()

        if existing_friendship:
            QMessageBox.information(self, "Info", "You are already friends with this user.")
            connection.close()
            return

        # Check if a request already exists
        cursor.execute(
            """
            SELECT id FROM friend_requests
            WHERE sender_id = ? AND receiver_id = ? AND status = 'pending'
            """,
            (sender_id, receiver_id),
        )
        existing_request = cursor.fetchone()

        if existing_request:
            QMessageBox.information(self, "Info", "You have already sent a request to this user.")
        else:
            try:
                # Insert a new friend request
                cursor.execute(
                    "INSERT INTO friend_requests (sender_id, receiver_id) VALUES (?, ?)",
                    (sender_id, receiver_id),
                )
                connection.commit()
                QMessageBox.information(self, "Success", "Friend request sent!")
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Error", f"Failed to send friend request: {str(e)}")
    else:
        QMessageBox.warning(self, "Error", "Sorry, the user is not registered to our system yet.")

    connection.close()

def load_friends(user_id):
    """Load the friends of the logged-in user."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    query = """
        SELECT u.name, u.id
        FROM friends f
        JOIN users u ON u.id = f.friend_id
        WHERE f.user_id = ?
    """
    cursor.execute(query, (user_id,))
    friends = cursor.fetchall()
    print(f"List of friends from db_handler_friends.py {friends}")
    return friends

def check_friend_requests(user_id, self=None):
    """Check and display pending friend requests for the logged-in user."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    query = """
        SELECT u.name
        FROM friend_requests fr
        JOIN users u ON u.id = fr.sender_id
        WHERE fr.receiver_id = ? AND fr.status = 'pending'
    """
    cursor.execute(query, (user_id,))
    requests = cursor.fetchall()

    connection.close()

    if requests:
        message = "You have friend requests from:\n" + "\n".join([req[0] for req in requests])
        reply = QMessageBox.question(
            self, "Friend Requests", message + "\nDo you want to respond now?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            respond_to_friend_requests(user_id)
            print(f"Responding to friend requests for user from db_handler_friends.py {user_id}")


def respond_to_friend_requests(user_id, self=None):
    """Respond to pending friend requests."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    # Retrieve pending friend requests
    query = """
        SELECT fr.id, u.id, u.name
        FROM friend_requests fr
        JOIN users u ON u.id = fr.sender_id
        WHERE fr.receiver_id = ? AND fr.status = 'pending'
    """
    cursor.execute(query, (user_id,))
    requests = cursor.fetchall()

    print(f"Pending requests: {requests}")

    for request_id, sender_id, sender_name in requests:
        reply = QMessageBox.question(
            self, "Friend Request", f"{sender_name} wants to be your friend. Accept?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Update the friend_requests table and add to friends
            cursor.execute("UPDATE friend_requests SET status = 'accepted' WHERE id = ?", (request_id,))
            cursor.execute(
                "INSERT INTO friends (user_id, friend_id) VALUES (?, ?), (?, ?)",
                (user_id, sender_id, sender_id, user_id)
            )

            # Fetch name by id and add to notifications
            cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
            sender_name = cursor.fetchone()
            sender_name = sender_name[0]


            # Add a notification for the sender
            notification_message = f"{sender_name} accepted your friend request!"
            cursor.execute(
                "INSERT INTO notifications (user_id, message) VALUES (?, ?)",
                (sender_id, notification_message)
            )
            connection.commit()
        else:
            # Reject the friend request
            cursor.execute("UPDATE friend_requests SET status = 'rejected' WHERE id = ?", (request_id,))
            connection.commit()

    connection.close()

def fetch_notifications(user_id, table: str):
    """Fetch unread notifications for a user."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    query = f"""
        SELECT id, message, created_at
        FROM {table}
        WHERE user_id = ? AND is_read = 0
        ORDER BY created_at DESC
    """
    cursor.execute(query, (user_id,))
    notifications = cursor.fetchall()

    connection.close()
    return notifications

def mark_notifications_as_read(user_id, table: str):
    """Mark all notifications as read for a user."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    query = f"UPDATE {table} SET is_read = 1 WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    connection.commit()

    connection.close()

def save_message(user_id, selected_friend, message_content, self=None):
    """Handles saving messages."""
    # Save the message to the database
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (?, ?, ?)
            """,
            (user_id, selected_friend, message_content),
        )
        QMessageBox.information(self, "Success", "Message sent successfully!")
        # storing notification for the receiver
        # Fetch sender name by id and add to notifications
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        sender_name = cursor.fetchone()
        sender_name = sender_name[0]

        # Add a notification for the sender
        notification_message = f"{sender_name} sent you a message!"
        cursor.execute(
            """
            INSERT INTO message_notifications (user_id, message)
            VALUES (?, ?)
            """,
            (selected_friend, notification_message),
        )
        connection.commit()

    except sqlite3.Error as e:
        QMessageBox.warning(self, "Error", f"Failed to send message: {str(e)}")
    finally:
        connection.close()

def load_chat_history_db(friend_id, user_id, self=None):
    """Loads the chat history between the current user and the selected friend."""
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT sender_id, content, timestamp, message_type  FROM messages
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
            """,
            (user_id, friend_id, friend_id, user_id),
        )
        chat_history = cursor.fetchall()
        return chat_history
    except sqlite3.Error as e:
        QMessageBox.warning(self, "Error", f"Failed to load chat history: {str(e)}")
        return []

    finally:
        connection.close()

def check_for_new_messages(user_id, selected_friend):
    """Checks for new messages from the database."""
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT sender_id, content, timestamp FROM messages
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp DESC LIMIT 1
            """,
            (user_id, selected_friend, selected_friend, user_id),
        )
        latest_message = cursor.fetchone()
        return latest_message

    except sqlite3.Error as e:
        print(f"Failed to check for new messages: {str(e)}")
    finally:
        connection.close()

def save_file_message(sender_id, receiver_id, file_data, file_type, file_name):
    """
    Saves a file (image or document) as a message in the database.

    The file's binary data is encoded into a base64 string and then stored in the
    'content' column as a JSON object containing the file name and encoded data.

    Parameters:
        sender_id (int): The ID of the user sending the file.
        receiver_id (int): The ID of the friend receiving the file.
        file_data (bytes): The binary data of the file.
        file_type (str): The type of the file, e.g., 'image' or 'doc'.
        file_name (str): The original name of the file.
    """
    # Encode the binary file data to a base64 string
    encoded_data = base64.b64encode(file_data).decode('utf-8')

    # Prepare the JSON content with file metadata
    content_dict = {
        "file_name": file_name,
        "data": encoded_data
    }
    content_json = json.dumps(content_dict)

    # Insert the message into the messages table
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = """
            INSERT INTO messages (sender_id, receiver_id, content, message_type)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (sender_id, receiver_id, content_json, file_type))
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if conn:
            conn.close()


def get_profile_picture_path_from_db(user_id):
    """
    Fetches the profile picture path for a user from the database.
    If no path exists, returns the default placeholder path.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: The path to the profile picture or a default placeholder.
    """
    # Define the default placeholder image path
    default_placeholder_path = "assets/logo.jpg"

    # Establish connection to the SQLite database
    try:
        connection = db_handler.create_connection()
        cursor = connection.cursor()

        # Query to fetch the image path
        query = "SELECT image_path FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        # Check if a result is found and return the path, otherwise return the default
        if result and result[0]:
            return result[0]
        else:
            return default_placeholder_path
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return default_placeholder_path
    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()

def update_profile_picture_in_db(user_id, image_path, self=None):
    """
    Updates the profile picture path for a user in the database.

    Args:
        user_id (int): The ID of the user.
        image_path (str): The new profile picture path.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        # Establish connection to the SQLite database
        connection = db_handler.create_connection()
        cursor = connection.cursor()

        # Update query
        query = "UPDATE users SET image_path = ? WHERE id = ?"
        cursor.execute(query, (image_path, user_id))

        # Commit changes
        connection.commit()

        # Check if the update was successful
        if cursor.rowcount > 0:
            QMessageBox.information(self, "Success", "Profile picture updated successfully!")
            print(f"Successfully updated profile picture for user_id: {user_id}")
            return True
        else:
            print(f"No rows updated. Check if user_id {user_id} exists.")
            return False

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()

def save_profile_changes(dialog, user_id, new_name, new_number, self=None):
    """
    Saves changes to the user's profile (name and number) in the database.

    Args:
        dialog (QDialog): The dialog instance that initiated the change.
        user_id (int): The ID of the user.
        new_name (str): The new name of the user.
        new_number (str): The new phone number of the user.

    Returns:
        None
    """
    try:
        # Establish connection to the SQLite database
        connection = db_handler.create_connection()
        cursor = connection.cursor()

        # Update query
        query = "UPDATE users SET name = ?, phone_number = ? WHERE id = ?"
        cursor.execute(query, (new_name, new_number, user_id))

        # Commit changes
        connection.commit()

        # Check if the update was successful
        if cursor.rowcount > 0:
            print(f"Profile updated successfully for user_id: {user_id}")
            QMessageBox.information(self, "Success", "Profile updated successfully!")


            # Accept the dialog (close it)
            dialog.accept()
        else:
            print(f"No rows updated. Check if user_id {user_id} exists.")
            dialog.reject()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        dialog.reject()

    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()


def update_profile_in_db(user_id, name, number, self=None):
    """
    Updates the profile details (name and phone number) in the database.

    Args:
        user_id (int): The ID of the user whose profile is being updated.
        name (str): The new name of the user.
        number (str): The new phone number of the user.

    Returns:
        None
    """
    try:
        # Connect to the SQLite database
        connection = db_handler.create_connection()
        cursor = connection.cursor()

        # Update query
        query = "UPDATE users SET name = ?, phone_number = ? WHERE id = ?"
        cursor.execute(query, (name, number, user_id))

        # Commit changes
        connection.commit()

        # Check if the update was successful
        if cursor.rowcount > 0:
            print(f"Profile updated in database: Name={name}, Number={number}")
            QMessageBox.information(self, "Success", "Profile updated successfully!")
        else:
            print(f"Profile update failed. Check if user_id {user_id} exists in the database.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()
