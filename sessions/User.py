#session
class User:
    def __init__(self, name, phone_number, user_id=None):
        self.__name = name
        self.__phone_number = phone_number
        self.__user_id = user_id

    def get_name(self):
        return self.__name

    def get_phone_number(self):
        return self.__phone_number

    def set_name(self, name):
        self.__name = name

    def set_user_id(self, user_id):
        self.__user_id = user_id

    def get_user_id(self):
        return self.__user_id

    def set_phone_number(self, phone_number):
        self.__phone_number = phone_number

    def __str__(self):
        return f"Name: {self.__name}, Phone Number: {self.__phone_number}"

    def __repr__(self):
        return f"User('{self.__name}', '{self.__phone_number}')"