# manager_window.py
class ManagerWindow:
    def __init__(self):
        self.login_window = None
        self.signup_window = None

    def open_login_window(self):
        # Lazy import of LoginWindow to avoid circular imports
        from auth_view.login_window import LoginWindow

        if self.login_window is None:
            self.login_window = LoginWindow()

        self.login_window.show()
        if self.signup_window:
            self.signup_window.close()

    def open_signup_window(self):
        # Lazy import of SignupWindow to avoid circular imports
        from auth_view.signup_window import AuthWindow

        if self.signup_window is None:
            self.signup_window = AuthWindow()

        self.signup_window.show()
        if self.login_window:
            self.login_window.close()
