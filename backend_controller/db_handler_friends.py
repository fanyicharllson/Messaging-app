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
        SELECT u.name
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

            print(f"Sender name from db_handler_friends.py {sender_name}")

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

def fetch_notifications(user_id):
    """Fetch unread notifications for a user."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    query = """
        SELECT id, message, created_at
        FROM notifications
        WHERE user_id = ? AND is_read = 0
        ORDER BY created_at DESC
    """
    cursor.execute(query, (user_id,))
    notifications = cursor.fetchall()

    connection.close()
    return notifications


def mark_notifications_as_read(user_id):
    """Mark all notifications as read for a user."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    query = "UPDATE notifications SET is_read = 1 WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    connection.commit()

    connection.close()

