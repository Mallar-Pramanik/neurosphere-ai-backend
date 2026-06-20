"""
Authentication Service - JWT tokens and user authentication
Fixed version with password length validation for bcrypt's 72-byte limit
"""

import logging
from datetime import datetime, timedelta
from pkgutil import get_data
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import settings
from models import User
from database import get_db

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# Security scheme
security = HTTPBearer()

# Constants
MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_LENGTH = 8


class PasswordValidationError(Exception):
    """Custom exception for password validation errors"""
    pass


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def validate_password_length(password: str) -> None:
        """
        Validate password length is within bcrypt's 72-byte limit

        Args:
            password: The password to validate

        Raises:
            PasswordValidationError: If password exceeds 72 bytes
        """
        password_bytes = password.encode('utf-8')

        if len(password_bytes) > MAX_PASSWORD_BYTES:
            raise PasswordValidationError(
                f"Password cannot exceed {MAX_PASSWORD_BYTES} bytes. "
                f"Your password is {len(password_bytes)} bytes. "
                f"Please use a shorter password."
            )

        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordValidationError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
            )

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password with length validation

        Args:
            password: The password to hash

        Returns:
            Hashed password

        Raises:
            PasswordValidationError: If password is invalid
        """
        AuthService.validate_password_length(password)
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    def register_user(
        db: Session,
        user_data
    ) -> User:
        """Register new user with password validation"""
        try:
            # Validate password before checking database
            AuthService.validate_password_length(user_data.password)

            # Check if user exists
            existing_user = db.query(User).filter(
                (User.email == user_data.email) | (
                    User.username == user_data.username)
            ).first()

            if existing_user:
                raise ValueError(
                    "User with this email or username already exists")

            # Create new user with hashed password
            logger.info(f"PASSWORD RECEIVED: {user_data.password}")
            logger.info(f"PASSWORD TYPE: {type(user_data.password)}")
            logger.info(f"PASSWORD LENGTH: {len(str(user_data.password))}")
            hashed_password = AuthService.hash_password(str(user_data.password))

            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=True
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"✅ User registered: {user.email}")
            return user

        except PasswordValidationError as e:
            logger.warning(f"Password validation failed: {str(e)}")
            raise ValueError(str(e))
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def login_user(
        db: Session,
        email: str,
        password: str
    ) -> str:
        """Login user and return token"""
        try:
            # Find user
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                raise ValueError("Invalid email or password")
            
            # Verify password
            logger.info(f"User found: {user.email}")
            logger.info(f"Hash starts with: {user.hashed_password[:30]}")
            if not AuthService.verify_password(password, user.hashed_password):
                raise ValueError("Invalid email or password")
            
            # Check if active
            if not user.is_active:
                raise ValueError("User account is inactive")
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create token
            token = AuthService.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            logger.info(f"✅ User logged in: {user.email}")
            return token
            
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Get current authenticated user"""
        token = credentials.credentials
        
        try:
            # Verify token
            payload = AuthService.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Get user from database
            user = db.query(User).filter(User.id == int(user_id)).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    @staticmethod
    def refresh_token(
        current_user: User
    ) -> str:
        """Refresh user token"""
        token = AuthService.create_access_token(
            data={"sub": str(current_user.id), "email": current_user.email}
        )
        return token
    
    @staticmethod
    def logout_user(
        db: Session,
        current_user: User
    ) -> bool:
        """Logout user (optional - can invalidate token in blacklist)"""
        logger.info(f"✅ User logged out: {current_user.email}")
        return True