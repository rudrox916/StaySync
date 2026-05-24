from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import query_db

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        """Fetch a User by ID using raw SQL."""
        row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                role=row['role'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_username(username):
        """Fetch a User by username using raw SQL."""
        row = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                role=row['role'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def get_by_email(email):
        """Fetch a User by email address using raw SQL."""
        row = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                role=row['role'],
                created_at=row['created_at']
            )
        return None

    @staticmethod
    def create(username, email, password, role='customer'):
        """Create a new user in the database using raw SQL."""
        from db import insert_db
        password_hash = generate_password_hash(password)
        query = "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)"
        user_id = insert_db(query, (username, email, password_hash, role))
        return User.get(user_id)

    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
