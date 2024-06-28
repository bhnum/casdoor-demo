import datetime
from typing import Annotated

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]
created_timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.current_timestamp()
    ),
]
updated_timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    ),
]


class Base(DeclarativeBase, AsyncAttrs):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    def patch(self, **update_dict: dict) -> None:
        """Partial update of an object with a simple and clear syntax"""
        for prop_name, value in update_dict.items():
            column = self.__table__.columns.get(prop_name)
            if column is not None and column.primary_key:
                raise ValueError("Primary key passed in patch update data")

            setattr(self, prop_name, value)


class Book(Base):
    __tablename__ = "book"

    id: Mapped[intpk]
    name: Mapped[str]
    author: Mapped[str]
    content: Mapped[str]
    creator_user_id: Mapped[str]
    modifier_user_id: Mapped[str]
    created: Mapped[created_timestamp]
    updated: Mapped[updated_timestamp]
