import uuid
import bcrypt


class User:
    def __init__(self, username, password_hash=None, user_id=None):
        self.user_id = user_id or str(uuid())
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password: str):
        """ password hash. """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str):
        """ compare password to stored hash. """
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
