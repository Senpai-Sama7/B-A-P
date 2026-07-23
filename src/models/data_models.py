"""
Data models for database entities and ORM.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from src.core.database import Base


class Dataset(Base):
    """Dataset entity representing uploaded data."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(256), nullable=True)
    created_by = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(50), default="active")
    metadata_ = Column("metadata", JSON, default={})
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)


class ETLJob(Base):
    """ETL job execution tracking."""

    __tablename__ = "etl_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(128), unique=True, index=True, nullable=False)
    dataset_id = Column(String(128), index=True, nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    parameters = Column(JSON, default={})
    result = Column(JSON, default={})
    created_by = Column(String(128), nullable=False)


class AIInsight(Base):
    """AI-generated insights."""

    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(String(128), unique=True, index=True, nullable=False)
    dataset_id = Column(String(128), index=True, nullable=False)
    insight_type = Column(String(50), nullable=False)  # summary, forecast, anomaly, etc.
    content = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), nullable=False)


class User(Base):
    """User entity for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    full_name = Column(String(256), nullable=True)
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
