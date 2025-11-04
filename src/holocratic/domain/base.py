"""Shared domain model utilities and mixins for SQLModel entities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlmodel import Field, SQLModel


class IdentifiedModel(SQLModel):
    """Mixin providing a UUID primary key."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column=Column(PGUUID(as_uuid=True), nullable=False),
    )


class TenantScopedModel(SQLModel):
    """Mixin adding the ``org_id`` tenant discriminator column."""

    org_id: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), nullable=False, index=True),
        foreign_key="organizations.id",
    )


class TimestampedModel(SQLModel):
    """Mixin providing creation and update timestamps."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class StatusModel(SQLModel):
    """Mixin providing a generic status column."""

    status: str = Field(
        default="active",
        sa_column=Column(String(length=32), nullable=False, index=True),
    )


class JSONMetadataModel(SQLModel):
    """Mixin providing a flexible JSON payload column."""

    properties: dict | None = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="{}"),
    )


__all__ = [
    "IdentifiedModel",
    "TenantScopedModel",
    "TimestampedModel",
    "StatusModel",
    "JSONMetadataModel",
]
