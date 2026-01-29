"""Auth module - minimal User and Group models for foreign key references."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from mitlist.db.base import Base, BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """User model - minimal for foreign key references."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Group(BaseModel, TimestampMixin):
    """Group model - minimal for foreign key references."""

    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by_id: Mapped[int] = mapped_column(nullable=False)


class CommonItemConcept(BaseModel, TimestampMixin):
    """Common item concept - minimal for foreign key references."""

    __tablename__ = "common_item_concepts"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
