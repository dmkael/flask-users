from flask import session
from uuid import uuid4


class UsersRepo:
    def __init__(self, username):
        self.db_name = f"{username}" + "db"

        if self.db_name not in session:
            session[self.db_name] = {}

    def content(self):
        return session[self.db_name]

    def show_name(self):
        return self.db_name

    def save_user(self, user: dict, user_id=None):
        if not user.get('name') or not user.get('email'):
            raise Exception(f"Wrong data: {user}")
        if not user_id:
            user_id = str(uuid4())
        session[self.db_name][user_id] = user
        session[self.db_name] = session[self.db_name]

    def find(self, user_id):
        return session[self.db_name].get(user_id)

    def delete_user(self, user_id):
        del session[self.db_name][user_id]
