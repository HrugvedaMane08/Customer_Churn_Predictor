import os
import sys
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Depends, status, Request

from app.schemas.auth_schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    ForgotPasswordSchema,
    AuthResponseSchema,
    ResetPasswordSchema
)
from src.logger import logging

router = APIRouter()

# Share the same SQLite database in the artifacts directory
DB_PATH = os.path.join("artifacts", "predictions.db")

# SMTP Server Configurations
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SENDER = os.getenv("SMTP_SENDER", SMTP_USERNAME)

def init_auth_db():
    """
    Initializes the SQLite tables for users, user_sessions, and password_resets if they do not exist.
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
        
        # 3. Create Password Resets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                email TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        logging.info("SQLite auth database tables (users, user_sessions, password_resets) initialized successfully.")
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
# SMTP Email Sending Helper
# ==========================================
def send_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Sends a password reset link to the user's email using configured SMTP.
    Returns True if successfully sent, False otherwise.
    """
    if not all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD]):
        logging.warning("SMTP mailing details not fully configured. Email was not sent.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_SENDER
        msg["To"] = to_email
        msg["Subject"] = "Reset Your ChurnPredict AI Password"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #f8fafc; padding: 2rem;">
            <div style="max-width: 550px; margin: 0 auto; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 2.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <h2 style="color: #4f46e5; margin-top: 0;">Password Reset Request</h2>
                <p>Hello,</p>
                <p>We received a request to reset the password associated with your account on ChurnPredict AI.</p>
                <p>Click the button below to reset your password. This link is valid for <strong>1 hour</strong>:</p>
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="{reset_link}" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 0.8rem 1.8rem; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);">Reset Password</a>
                </div>
                <p style="color: #64748b; font-size: 0.85rem;">If the button doesn't work, copy and paste this URL into your browser:</p>
                <p style="color: #64748b; font-size: 0.85rem; word-break: break-all; font-family: monospace; background: #f1f5f9; padding: 0.8rem; border-radius: 6px;">{reset_link}</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 2rem 0;" />
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0;">If you did not request a password reset, you can safely ignore this email.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))
        
        # Connect to server via TLS
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_SENDER, to_email, msg.as_string())
        server.quit()
        logging.info(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send password reset email: {str(e)}")
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

@router.post("/forgot-password", summary="Generate a password reset token and send via email")
def forgot_password(payload: ForgotPasswordSchema, request: Request):
    """
    Finds a user profile by email, generates a temporary reset token,
    stores it with a 1-hour expiry, and emails the reset link.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (payload.email.lower(),))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="No account found with this email address."
            )
            
        # Generate secure random token
        reset_token = secrets.token_hex(24)
        expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
        
        # Save token in password_resets table
        cursor.execute("""
            INSERT OR REPLACE INTO password_resets (email, token, expires_at)
            VALUES (?, ?, ?)
        """, (payload.email.lower(), reset_token, expires_at))
        conn.commit()
        conn.close()
        
        # Determine base URL for reset page:
        # In a deployment environment where frontend is served by FastAPI, the base_url points
        # to the FastAPI host (e.g. http://localhost:8000/ or http://your-app.onrender.com/).
        # For local dev sandbox where Next.js runs on port 3000, we check request referer or fallback to port 8000 origin.
        origin = request.headers.get("referer") or str(request.base_url)
        base_url = origin.split("?")[0].rstrip("/")
        # If the origin is backend, but we want the link to reach frontend pages:
        if "8000" in base_url and not request.headers.get("referer"):
            # fallback to 3000 for local dev convenience
            reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        else:
            reset_link = f"{base_url}/reset-password?token={reset_token}"
            
        # Trigger email delivery
        email_sent = send_reset_email(payload.email.lower(), reset_link)
        
        logging.info(f"Password reset token created for {payload.email}. Link: {reset_link}")
        
        response = {
            "status": "Success",
            "email_sent": email_sent,
            "message": "A password reset link has been sent to your email address." if email_sent 
                       else "Password reset link created successfully (Sandbox: check terminal logs)."
        }
        
        # Sandbox mode fallback: Return the link directly in API so users can click/test instantly
        # without SMTP setups!
        if not email_sent:
            response["reset_link"] = reset_link
            
        return response
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Forgot password token error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/reset-password", summary="Verify reset token and update user password")
def reset_password(payload: ResetPasswordSchema):
    """
    Validates a password reset token, updates the corresponding user's
    password hash, and removes the reset token.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Fetch token details
        cursor.execute("""
            SELECT email, expires_at FROM password_resets WHERE token = ?
        """, (payload.token,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired password reset token."
            )
            
        email, expires_at_str = row
        
        # 2. Check expiry
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", ""))
        if datetime.utcnow() > expires_at:
            cursor.execute("DELETE FROM password_resets WHERE token = ?", (payload.token,))
            conn.commit()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="The password reset link has expired. Please request a new one."
            )
            
        # 3. Update password hash
        pw_hash = hash_password(payload.password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (pw_hash, email))
        
        # 4. Invalidate sessions and delete the used reset token
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        if user_row:
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_row[0],))
            
        cursor.execute("DELETE FROM password_resets WHERE token = ?", (payload.token,))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Password reset completed for email: {email}")
        return {
            "status": "Success",
            "message": "Your password has been successfully reset. You may now sign in."
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Reset password error: {str(e)}")
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
