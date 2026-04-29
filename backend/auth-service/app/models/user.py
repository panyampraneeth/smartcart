from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key — auto-incrementing integer
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # User details
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Role — buyer or seller
    role: Mapped[str] = mapped_column(String, default="buyer", nullable=False)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps — set automatically by the database
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
