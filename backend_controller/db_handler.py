import sqlite3

# Path to the SQLite database file
DB_PATH = "C:/Users/NTECH/OneDrive/Desktop/CREATED DATABASES/message.db"


def create_connection():
    """
    Create a database connection.

    Returns:
        sqlite3.Connection: A connection object for the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def insert_user(name, phone_number):
    """Insert a new user into the users table."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, phone_number) VALUES (?, ?)", (name, phone_number))
    conn.commit()
    conn.close()


def check_user_exists(name, phone_number):
    """Check if a user with the given name or phone number exists in the database."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE name = ? OR phone_number = ?",
        (name, phone_number)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None


def validate_user_data(name, phone_number):
    """Validate name and phone number."""
    if len(name.strip()) == 0 or len(phone_number.strip()) == 0:
        return False, "Name or phone number cannot be empty."
    if len(phone_number) < 9:
        return False, "Phone number must be at least 9 digits."
    return True, ""

def login_user(name, phone):
        """
        Checks if a user with the given name and phone number exists in the database.

        :param name: The name of the user.
        :param phone: The phone number of the user.
        :return: True if the user exists, False otherwise.
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE name = ? AND phone_number = ?", (name, phone)
                )
                user = cursor.fetchone()
                return user is not None
            except sqlite3.Error as e:
                print(f"Error during login: {e}")
                return False
            finally:
                conn.close()
