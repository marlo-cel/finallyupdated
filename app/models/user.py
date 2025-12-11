import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any


class User:
    """
    Represents a user in the system.

    Think of this like a profile card that stores all user information
    and knows how to do things like check passwords and validate data.

    Attributes:
        id (int): Unique identifier for the user
        username (str): User's login name
        password_hash (str): Encrypted password (never stores plain text!)
        role (str): User's role ('user' or 'admin')
        created_at (datetime): When the account was created
    """

    # Class variable - like a shared rulebook everyone follows
    VALID_ROLES = ['user', 'admin']
    MIN_USERNAME_LENGTH = 3
    MIN_PASSWORD_LENGTH = 6

    def __init__(self, username: str, password_hash: str, role: str = 'user',
                 user_id: Optional[int] = None, created_at: Optional[datetime] = None):
        """
        Initialize a new User object.

        Args:
            username: The user's unique username
            password_hash: Already hashed password (not plain text)
            role: User's role in the system
            user_id: Optional ID (None for new users)
            created_at: When user was created (auto-set if None)
        """
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role if role in self.VALID_ROLES else 'user'
        self.created_at = created_at or datetime.now()

    @classmethod
    def create_new(cls, username: str, plain_password: str, role: str = 'user') -> 'User':
        """
        Factory method to create a new user with password hashing.

        This is like a special recipe that creates a User object and automatically
        encrypts the password - so you don't have to remember to do it separately!

        Args:
            username: Desired username
            plain_password: Plain text password (will be hashed)
            role: User role

        Returns:
            New User object with hashed password

        Raises:
            ValueError: If validation fails
        """
        # Validate before creating
        cls.validate_username(username)
        cls.validate_password(plain_password)

        # Hash the password
        hashed = cls.hash_password(plain_password)

        return cls(username=username, password_hash=hashed, role=role)

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Like putting the password through a one-way scrambler - you can check
        if a password matches, but you can never get the original back!

        Args:
            plain_password: Plain text password

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str) -> bool:
        """
        Check if a plain password matches this user's stored hash.

        Args:
            plain_password: Password to check

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    @classmethod
    def validate_username(cls, username: str) -> None:
        """
        Validate username meets requirements.

        Args:
            username: Username to validate

        Raises:
            ValueError: If username is invalid
        """
        if not username:
            raise ValueError("Username cannot be empty")

        if len(username) < cls.MIN_USERNAME_LENGTH:
            raise ValueError(f"Username must be at least {cls.MIN_USERNAME_LENGTH} characters")

        if ',' in username or ' ' in username:
            raise ValueError("Username cannot contain commas or spaces")

    @classmethod
    def validate_password(cls, password: str) -> None:
        """
        Validate password meets requirements.

        Args:
            password: Password to validate

        Raises:
            ValueError: If password is invalid
        """
        if not password:
            raise ValueError("Password cannot be empty")

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters")

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin'

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary (useful for JSON/database storage).

        Returns:
            Dictionary representation of user
        """
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create User object from dictionary.

        Args:
            data: Dictionary with user data

        Returns:
            User object
        """
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])

        return cls(
            username=data['username'],
            password_hash=data['password_hash'],
            role=data.get('role', 'user'),
            user_id=data.get('id'),
            created_at=created_at
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"User(id={self.id}, username='{self.username}', role='{self.role}')"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.username} ({self.role})"