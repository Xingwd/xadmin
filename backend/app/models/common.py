from datetime import datetime
from typing import Annotated

from sqlmodel import Field, text

TableRecordCreatedDateTime = Annotated[
    datetime,
    Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    ),
]

TableRecordUpdatedDateTime = Annotated[
    datetime,
    Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={"onupdate": lambda: datetime.now()},
    ),
]
