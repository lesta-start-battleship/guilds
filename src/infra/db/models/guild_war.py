from sqlalchemy import Enum as SqlEnum, Column, Integer, String, ForeignKey, DateTime
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import TIMESTAMP

from infra.db.database import Base

class WarStatus(str, Enum):
    pending = "pending"    # ожидание подтверждения
    active = "active"      # война началась
    finished = "finished"  # война завершена
    declined = "declined"  # отклонено
    canceled = "canceled"  # отменено инициатором
    expired = "expired"    # просрочено автоматически

class GuildWarRequest(Base):
    __tablename__ = "guild_war_requests"

    id = Column(Integer, primary_key=True, index=True)
    initiator_guild_id = Column(Integer, ForeignKey("guilds.id"))
    target_guild_id = Column(Integer, ForeignKey("guilds.id"))
    status = Column(SqlEnum(WarStatus, name="warstatus"), default=WarStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class GuildWarRequestHistory(Base):
    __tablename__ = "guild_war_requests_history"

    id = Column(Integer, primary_key=True, index=True)
    war_id = Column(Integer, index=True, nullable=False)
    initiator_guild_id = Column(Integer, index=True)
    target_guild_id = Column(Integer, index=True)
    status = Column(SqlEnum(WarStatus, name="warstatus"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    finished_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))