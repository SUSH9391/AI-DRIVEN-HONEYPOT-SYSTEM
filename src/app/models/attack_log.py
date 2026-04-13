from sqlalchemy import String, Float, DateTime, func, Index, ForeignKey, JSON # Added JSON here
from sqlalchemy.dialects.postgresql import INET, UUID
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from typing import Optional, Dict, Any

class AttackLog(Base):
    __tablename__ = "attack_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, server_default=func.gen_random_uuid()
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ip: Mapped[str] = mapped_column(INET, nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String)
    method: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=False)
    query: Mapped[Optional[str]] = mapped_column(String)
    
    # FIX 1: Add JSON type here
    body: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON) 
    
    attack_type: Mapped[Optional[str]] = mapped_column(String)  # 'sqli' | 'xss' etc.
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    rule_matched: Mapped[Optional[str]] = mapped_column(String)
    
    # FIX 2: Add JSON type here
    fake_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("sessions.id")
    )
    country: Mapped[Optional[str]] = mapped_column(String)
    asn: Mapped[Optional[str]] = mapped_column(String)

    # Relationships
    session = relationship("Session", back_populates="attack_logs")

    __table_args__ = (
        Index("idx_attack_logs_ip", "ip"),
        Index("idx_attack_logs_created_at", "created_at"),
        Index("idx_attack_logs_type", "attack_type"),
        Index("idx_attack_logs_session", "session_id"),
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, server_default=func.gen_random_uuid()
    )
    ip: Mapped[str] = mapped_column(INET, nullable=False)
    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    event_count: Mapped[int] = mapped_column(default=0)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    
    # FIX 3: Add JSON type here
    fingerprint: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    attack_logs = relationship("AttackLog", back_populates="session")

    __table_args__ = (Index("idx_sessions_ip", "ip", unique=True),)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default="admin")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )