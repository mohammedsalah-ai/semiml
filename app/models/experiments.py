"""
Define The Experiement model.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, UUID, ForeignKey, Boolean

from app.models.base import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    model_path: Mapped[str] = mapped_column(String, nullable=False, default="")
    model_schema: Mapped[str] = mapped_column(String, nullable=False, default="")
    target_col: Mapped[str] = mapped_column(String, nullable=False)
    live: Mapped[str] = mapped_column(Boolean, nullable=False, default=False)

    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="experiments")

    file_id: Mapped[uuid.UUID] = mapped_column(String, nullable=False)
