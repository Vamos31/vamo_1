from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Enum, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        # チームの日程一覧を、開始日時の順に引くので索引をつける
        Index("ix_events_team_id_starts_at", "team_id", "starts_at"),
        CheckConstraint("ends_at IS NULL OR ends_at > starts_at", name="ends_after_starts"),
        CheckConstraint(
            "attendance_deadline IS NULL OR attendance_deadline <= starts_at",
            name="deadline_before_start",
        ),
    )

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
    # 1人1日程1出欠。UPSERT (ON CONFLICT (event_id, user_id)) の対象になる
    __table_args__ = (
        UniqueConstraint("event_id", "user_id"),
        # 「自分の出欠」を user_id から引く
        Index("ix_attendances_user_id", "user_id"),
    )

    # フェーズ3で user_id を NULL 可にする (助っ人対応) ため、複合主キーにせず代理キー id を持つ
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(
        Enum("attending", "not_attending", "undecided", name="attendance_status",
             native_enum=False, create_constraint=True)
    )
    comment: Mapped[str | None] = mapped_column(Text)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
