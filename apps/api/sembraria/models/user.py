"""
Modelo User.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    PRODUCTOR = "productor"
    COOPERATIVA = "cooperativa"
    EXTENSIONISTA = "extensionista"
    GOBIERNO = "gobierno"


from sembraria.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.PRODUCTOR,
        index=True,
    )
    organization = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    sms_notifications = Column(Boolean, nullable=False, default=False)
    email_notifications = Column(Boolean, nullable=False, default=True)
    whatsapp_notifications = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
