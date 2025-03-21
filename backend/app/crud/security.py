from sqlmodel import Session

from app.core.security import verify_password
from app.crud.user import get_user_by_username
from app.models.user import User


def authenticate(*, session: Session, username: str, password: str) -> User | None:
    db_user = get_user_by_username(session=session, username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
