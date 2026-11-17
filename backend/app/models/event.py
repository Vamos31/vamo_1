from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Event(Base):
    __tablename__ = "events"
    # チームの日程一覧を、開始日時の順に引くので索引をつける
    __table_args__ = (Index("ix_events_team_id_starts_at", "team_id", "starts_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    type: Mapped[str] = mapped_column(
        Enum("match", "practice", "other", name="event_type",
             native_enum=False, create_constraint=True)
    )
    title: Mapped[str] = mapped_column(Text)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    attendance_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Attendance(Base):
    __tablename__ = "attendances"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    status: Mapped[str] = mapped_column(
        Enum("attending", "not_attending", "undecided", name="attendance_status",
             native_enum=False, create_constraint=True)
    )
    comment: Mapped[str | None] = mapped_column(Text)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
