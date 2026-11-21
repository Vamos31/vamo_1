from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Enum, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        # チーム単位のメンバー検索と、在籍幹事の人数を数える用。user_id 側は主キーの先頭列が担う
        Index("ix_team_members_team_id_role", "team_id", "role"),
        CheckConstraint("left_at IS NULL OR left_at >= joined_at", name="left_after_joined"),
    )

    # 複合主キー: (user_id, team_id) の組み合わせが一意 = 同じ人を同じチームに二重登録できない
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    role: Mapped[str] = mapped_column(Enum("admin", "member", name="member_role",
                                     native_enum=False, create_constraint=True))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Invitation(Base):
    __tablename__ = "invitations"
    # 幹事の招待リンク一覧 (チーム内で新しい順)
    __table_args__ = (Index("ix_invitations_team_id_created_at", "team_id", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    token: Mapped[str] = mapped_column(Text, unique=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
