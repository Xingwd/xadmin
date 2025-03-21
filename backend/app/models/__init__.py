from sqlmodel import SQLModel

# for 'alembic autogenerate' support
from . import link, operation_log, role, rule, security, user  # noqa


# Generic message
class Message(SQLModel):
    message: str
