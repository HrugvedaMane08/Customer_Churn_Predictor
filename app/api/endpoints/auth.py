import os
import sys
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Depends, status

from app.schemas.auth_schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    ForgotPasswordSchema,
    AuthResponseSchema
)
from src.logger import logging

router = APIRouter()

# Share the same SQLite database in the artifacts directory
DB_PATH = os.path.join("artifacts", "predictions.db")

def init_auth_db():
    """
    Initializes the SQLite tables for users and sessions if they do not exist.
    """
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Create Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Administrator'
            )
        """)
        
        # 2. Create User Sessions table for token management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        logging.info("SQLite auth database tables (users, user_sessions) initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize SQLite auth tables: {str(e)}")

# Initialize auth tables on load
init_auth_db()

# ==========================================
# Password Cryptography Helpers (PBKDF2)
# ==========================================
def hash_password(password: str) -> str:
    """
    Hashes a password securely using PBKDF2 HMAC with SHA-256 and a random salt.
    """
    salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return f"{salt}:{hash_bytes.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifies a password against a stored password hash.
    """
    try:
        salt, hash_hex = password_hash.split(":")
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )
        return hash_bytes.hex() == hash_hex
    except Exception:
        return False

# ==========================================
# Token Session Management Helpers
# ==========================================
def create_session(user_id: int) -> str:
    """
    Generates a secure session token valid for 30 days and stores it in SQLite.
    """
    token = secrets.token_hex(32)
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_sessions (token, user_id, expires_at)
        VALUES (?, ?, ?)
    """, (token, user_id, expires_at))
    conn.commit()
    conn.close()
    return token

# ==========================================
# API Endpoint Route Handlers
# ==========================================

@router.post("/signup", response_model=AuthResponseSchema, summary="Register a new user")
def signup(payload: UserRegisterSchema):
    """
    Checks if email already exists, stores user registration details,
    hashes the password, and returns a logged-in session.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (payload.email.lower(),))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="An account with this email address already exists."
            )
            
        # Hash password and insert
        pw_hash = hash_password(payload.password)
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (payload.name, payload.email.lower(), pw_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Auto-generate session token on successful register
        token = create_session(user_id)
        
        logging.info(f"New user registered: {payload.email} (ID: {user_id})")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user_id),
                "name": payload.name,
                "email": payload.email,
                "role": "Administrator"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during signup: {str(e)}"
        )

@router.post("/login", response_model=AuthResponseSchema, summary="Authenticate user login")
def login(payload: UserLoginSchema):
    """
    Validates user credentials against the password hash in SQLite,
    creates a session token, and returns the profile details.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password_hash, role FROM users WHERE email = ?", (payload.email.lower(),))
        row = cursor.fetchone()
        conn.close()
        
        if not row or not verify_password(payload.password, row[3]):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email address or password. Please try again."
            )
            
        user_id, name, email, _, role = row
        token = create_session(user_id)
        
        logging.info(f"User logged in successfully: {email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user_id),
                "name": name,
                "email": email,
                "role": role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during login: {str(e)}"
        )

@router.post("/forgot-password", summary="Reset user password and return a temporary credential")
def forgot_password(payload: ForgotPasswordSchema):
    """
    Finds a user profile by email and resets their password to a secure random temporary one.
    Returns the plain temporary password for demo copying.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (payload.email.lower(),))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            # To prevent username harvesting in production we could return 200, 
            # but for this specific demo platform, raising a clear 404 error is highly helpful to users.
            raise HTTPException(
                status_code=404,
                detail="No account found with this email address."
            )
            
        user_id = row[0]
        
        # Generate secure temporary password
        temp_password = "temp-" + secrets.token_hex(4)
        pw_hash = hash_password(temp_password)
        
        # Update database with new hash
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
        
        # Delete old sessions for security force-logout
        cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Temporary password generated for {payload.email}")
        return {
            "status": "Success",
            "message": "Your password has been successfully reset to a temporary credential.",
            "temporary_password": temp_password
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Forgot password reset error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during password reset: {str(e)}"
        )

# ==========================================
# Authentication Verification Dependency
# ==========================================
def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Dependency checking the Authorization header Bearer token against active SQLite sessions.
    Throws a 401 Unauthorized exception if token is missing, expired, or invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required to access this resource."
        )
        
    token = authorization.split(" ")[1]
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.role
            FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND datetime(s.expires_at) > datetime('now')
        """, (token,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired or token is invalid. Please sign in again."
            )
            
        return {
            "id": str(row[0]),
            "name": row[1],
            "email": row[2],
            "role": row[3]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Auth token check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session validation failed: {str(e)}"
        )
