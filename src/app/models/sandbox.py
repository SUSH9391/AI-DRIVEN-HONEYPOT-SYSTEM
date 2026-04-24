import uuid
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class SandboxSession(Base):
    __tablename__ = "sandbox_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    env_type: Mapped[str] = mapped_column(String, nullable=False)
    theme_template: Mapped[str] = mapped_column(String, nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)
    session_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attacks_detected: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sandbox_sessions")
    badges = relationship("Badge", back_populates="sandbox")
    attack_logs = relationship("AttackLog", back_populates="sandbox")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    badge_type: Mapped[str] = mapped_column(String, nullable=False)
    earned_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sandbox_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("sandbox_sessions.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="badges")
    sandbox = relationship("SandboxSession", back_populates="badges")
