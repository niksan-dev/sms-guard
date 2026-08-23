import secrets

from datetime import (
    datetime,
    timedelta
)

from database.connection import SessionLocal
from database.auth_session import AuthSession


SESSION_DURATION_MINUTES = 30


def create_login_session(user_id):

    db = SessionLocal()

    try:

        # Remove old expired sessions
        db.query(AuthSession).filter(
            AuthSession.expires_at < datetime.utcnow()
        ).delete()

        # Create secure random token
        token = secrets.token_urlsafe(48)

        expires_at = (
            datetime.utcnow()
            + timedelta(
                minutes=SESSION_DURATION_MINUTES
            )
        )

        auth_session = AuthSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )

        db.add(auth_session)

        db.commit()

        return token, expires_at

    finally:

        db.close()


def get_user_from_session(token):

    if not token:
        return None

    db = SessionLocal()

    try:

        auth_session = db.query(AuthSession).filter(
            AuthSession.token == token
        ).first()

        if not auth_session:

            return None

        # Session expired
        if auth_session.expires_at < datetime.utcnow():

            db.delete(auth_session)

            db.commit()

            return None

        user = auth_session.user

        # Copy data before closing database
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }

    finally:

        db.close()


def delete_login_session(token):

    if not token:
        return

    db = SessionLocal()

    try:

        db.query(AuthSession).filter(
            AuthSession.token == token
        ).delete()

        db.commit()

    finally:

        db.close()