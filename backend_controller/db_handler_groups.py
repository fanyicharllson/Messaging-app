import sqlite3

from PySide6.QtWidgets import QMessageBox

from backend_controller import db_handler
def add_group(dialog, user_id, selected_friends, group_name):
    """Add group to the database"""
    try:
        # Insert group into the database
        connection = db_handler.create_connection()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO groups (group_name, created_by) VALUES (?, ?)", (group_name, user_id))
        group_id = cursor.lastrowid

        # Add group members
        for friend_id in selected_friends:
            cursor.execute("INSERT INTO group_members (group_id, member_id) VALUES (?, ?)", (group_id, friend_id))


        sender_name = db_handler.fetch_user_name_by_id(user_id)

        notification_message = f"{sender_name} added you in {group_name} group!"
        cursor.execute( """ INSERT INTO message_notifications (user_id, message)
                VALUES (?, ?)
                """,
                (friend_id, notification_message),
        )
        connection.commit()

        QMessageBox.information(None, "Success", f"Group '{group_name}' created successfully! Click on message group icon to start charting with group.")
        dialog.accept()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to create group: {str(e)}")

def fetch_group(user_id):
    """Fetch group from the database"""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    # Fetch groups created by the user
    try:
        cursor.execute("SELECT id, group_name FROM groups WHERE created_by = ?", (user_id,))
        groups = cursor.fetchall()
        return groups

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Db error", f"Database error {str(e)}")

    finally:
        if connection:
            connection.close()

def fetch_group_message(group_id):
    """Fetch group message from the database"""
    # Fetch and display messages
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                    SELECT u.name, m.content, m.timestamp
                    FROM messages m
                    JOIN users u ON u.id = m.sender_id
                    WHERE m.receiver_id = ?
                    ORDER BY m.timestamp ASC
                """, (group_id,))
        messages = cursor.fetchall()
        return  messages

    except sqlite3.Error as e:
        QMessageBox.critical(None, "Db error", f"Database error {str(e)}")
        return []


    finally:
        if connection:
            connection.close()

def store_group_message(user_id, group_id, content):
    """Stores group message to the db"""
    try:
        connection = db_handler.create_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
                       (user_id, group_id, content))


        sender_name = db_handler.fetch_user_name_by_id(user_id)

        notification_message = f"Group message from {sender_name}"
        cursor.execute( """ INSERT INTO message_notifications (user_id, message)
                VALUES (?, ?)
                """,
                (user_id, notification_message),
        )
        connection.commit()
        return True

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to send message: {str(e)}")
        return

    finally:
        if connection:
            connection.close()

def fetch_group_members(group_id):
    """Fetch the members of a specific group."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    try:
        query = """
            SELECT u.name
            FROM group_members gm
            JOIN users u ON u.id = gm.member_id   
            WHERE gm.group_id = ?
        """
        #NB Line 106========================================================================
        cursor.execute(query, (group_id,))
        members = cursor.fetchall()
        connection.close()
        return members

    except sqlite3.Error as e:
        QMessageBox.critical(None, "DB error", f"{str(e)}")
        return []

    finally:
        connection.close()

def fetch_groups_for_user(user_id):
    """Fetch all groups the user is a part of or has created."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    try:
        query = """
               SELECT DISTINCT g.id, g.group_name
               FROM groups g
               LEFT JOIN group_members gm ON g.id = gm.group_id
               WHERE g.created_by = ? OR gm.member_id = ?;
           """
        cursor.execute(query, (user_id, user_id))
        groups = cursor.fetchall()
        print(f"Groups fetched for user {user_id}: {groups}")
        return groups
    except Exception as e:
        print(f"Error fetching groups for user: {e}")
        return []
    finally:
        connection.close()



def get_group_creator(group_id):
    """Fetch the name of the user who created the group."""
    connection = db_handler.create_connection()
    cursor = connection.cursor()

    try:
        query = """
            SELECT g.group_name, u.name AS creator_name
            FROM groups g
            JOIN users u ON g.created_by = u.id
            WHERE g.id = ?;
        """
        cursor.execute(query, (group_id,))
        result = cursor.fetchone()  # Fetch a single row
        if result:
            group_name, creator_name = result
            print(f"group_name:  {group_name}, creator_name: {creator_name}")
            return creator_name
        else:
            print(f"No group found with ID: {group_id}")
            return None
    except Exception as e:
        print(f"Error fetching group creator: {e}")
        return None
    finally:
        connection.close()

