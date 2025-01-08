from bson import ObjectId
import bcrypt
from db import db


class User:
    def __init__(self, username, password_hash=None, user_id=None, email = None):
        self.user_id = user_id or str(ObjectId())
        self.username = username
        self.password_hash = password_hash
        self.email = email

    def set_password(self, password: str):
        """ password hash. """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str):
        """ compare password to stored hash. """
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def save(self):
        """ save user in database. """
        user_data = {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
        }
        db.users.insert_one(user_data)


    @classmethod
    def search_id(Cls, user_id: str):
        """ find user by id. """
        user_data = db.users.find_one({"user_id": user_id})
        if user_data:
            return Cls(
                user_id=user_data["user_id"],
                username=user_data["username"],
                password_hash=user_data["password_hash"],
            )
        return None
    
    @classmethod
    def find_by_username_or_email(cls, identifier: str):
        """ find user by username or email. """
        user_data = db.users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
        if user_data:
            return cls(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                user_id=user_data["user_id"],
            )
        return None
    
    @classmethod
    def find_by_email(cls, email: str):
        """ find user by email. """
        user_data = db.users.find_one({"email": email})
        if user_data:
            return cls(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                user_id=user_data["user_id"],
            )
        return None