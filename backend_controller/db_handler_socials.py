import sqlite3
from datetime import datetime, timedelta

from PySide6.QtWidgets import QMessageBox
from backend_controller.db_handler import create_connection


def post_status(user_id, content, self=None):
    """
    Posts a new status for a user.

    Args:
        user_id (int): The ID of the user posting the status.
        content (str): The content of the status.

    Returns:
        None
    """
    expiration_time = datetime.now() + timedelta(hours=24)
    try:
        if not content.strip():
            print("Cannot post an empty status.")
            QMessageBox.information(self, "Empty Status", "Cannot post an empty status.")
            return

        # Connect to the SQLite database
        connection = create_connection()
        cursor = connection.cursor()

        # Insert status into the database
        query = "INSERT INTO statuses (user_id, content, timestamp, expiration_time) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (user_id, content, datetime.now(), expiration_time))

        # Commit changes
        connection.commit()

        print("Status posted successfully!")
        QMessageBox.information(self, "Success", "Status posted! Click the eye icon to see the status.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()


def get_statuses(user_id=None, self=None):
    """
    Fetches statuses from the database.

    Args:
        user_id (int, optional): The ID of the user to filter statuses. If None, fetches all statuses.

    Returns:
        list: A list of dictionaries containing status information.
    """
    try:
        # Connect to the SQLite database
        connection = create_connection()
        cursor = connection.cursor()

        if user_id:
            query = "SELECT s.content, s.timestamp, u.name FROM statuses s JOIN users u ON s.user_id = u.id WHERE s.user_id = ? ORDER BY s.timestamp DESC"
            cursor.execute(query, (user_id,))
        else:
            query = "SELECT s.content, s.timestamp, u.name FROM statuses s JOIN users u ON s.user_id = u.id ORDER BY s.timestamp DESC"
            cursor.execute(query)

        # Fetch all results
        statuses = cursor.fetchall()

        # Format as a list of dictionaries
        return [{"content": row[0], "timestamp": row[1], "user": row[2]} for row in statuses]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        # Ensure the connection is closed
        if 'connection' in locals() and connection:
            connection.close()


def get_friend_and_user_statuses(user_id):
    """
       Fetches statuses posted by the logged-in user and their friends, excluding expired ones.

       Args:
           user_id (int): The ID of the logged-in user.

       Returns:
           list: A list of dictionaries containing the name, content, and timestamp of statuses.
       """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        query = """
         SELECT s.content, s.timestamp, u.name, s.id, s.user_id, s.expiration_time
        FROM statuses s
        JOIN users u ON s.user_id = u.id
        WHERE (s.user_id = ? OR s.user_id IN (
            SELECT friend_id FROM friends WHERE user_id = ?
        ))
        AND (s.expiration_time > CURRENT_TIMESTAMP) -- Only fetch non-expired statuses
        ORDER BY s.timestamp DESC
        """
        cursor.execute(query, (user_id, user_id))

        statuses = cursor.fetchall()
        return [{"content": row[0], "timestamp": row[1], "user": row[2], "status_id": row[3], "user_id": row[4], "expiration_time": row[5]} for row in statuses]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        if connection:
            connection.close()


def like_status(status_id, user_id, self=None):
    """
    Likes a friend's status.

    Args:
        status_id (int): The ID of the status to like.
        user_id (int): The ID of the user liking the status.

    Returns:
        None
    """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check if the user has already liked this status
        check_query = "SELECT 1 FROM likes WHERE status_id = ? AND user_id = ?"
        cursor.execute(check_query, (status_id, user_id))
        if cursor.fetchone():
            QMessageBox.warning(self, "Already Liked", "You have already liked this status.")
            return

        query = "INSERT INTO likes (status_id, user_id, created_at) VALUES (?, ?, ?)"
        cursor.execute(query, (status_id, user_id, datetime.now()))
        connection.commit()

        print("Status liked successfully!")
        QMessageBox.information(self, "Liked", "Status liked!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if connection:
            connection.close()

def track_status_view(status_id, user_id):
    """
    Tracks when a user views a friend's status.

    Args:
        status_id (int): The ID of the status being viewed.
        user_id (int): The ID of the user viewing the status.
    """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check if the user has already viewed this status
        check_query = "SELECT 1 FROM views WHERE status_id = ? AND user_id = ?"
        cursor.execute(check_query, (status_id, user_id))
        if cursor.fetchone():
            return  # Already viewed, no need to add again

        # Add the view
        query = "INSERT INTO views (status_id, user_id) VALUES (?, ?)"
        cursor.execute(query, (status_id, user_id))
        connection.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if connection:
            connection.close()

def get_users_who_liked_status(status_id):
    """
    Fetches a list of users who liked a specific status.

    Args:
        status_id (int): The ID of the status.

    Returns:
        list: A list of user names.
    """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        query = """
        SELECT u.name
        FROM likes l
        JOIN users u ON l.user_id = u.id
        WHERE l.status_id = ?
        """
        cursor.execute(query, (status_id,))
        return [row[0] for row in cursor.fetchall()]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        if connection:
            connection.close()

def get_users_who_viewed_status(status_id):
    """
    Fetches a list of users who viewed a specific status.

    Args:
        status_id (int): The ID of the status.

    Returns:
        list: A list of user names.
    """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        query = """
        SELECT u.name
        FROM views v
        JOIN users u ON v.user_id = u.id
        WHERE v.status_id = ?
        """
        cursor.execute(query, (status_id,))
        return [row[0] for row in cursor.fetchall()]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        if connection:
            connection.close()


def delete_status(user_id, status_id):
    """
    Deletes a status from the database.
    """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Delete the status where user_id and status_id match
        query = "DELETE FROM statuses WHERE user_id = ? AND id = ?"
        cursor.execute(query, (user_id, status_id))
        connection.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if connection:
            connection.close()


def delete_expired_statuses():
    """
    Deletes statuses that have passed their expiration time.
    """
    try:
        connection = create_connection()
        cursor = connection.cursor()

        query = "DELETE FROM statuses WHERE expiration_time <= CURRENT_TIMESTAMP"
        cursor.execute(query)
        connection.commit()

        print("Expired statuses cleaned up.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if connection:
            connection.close()


