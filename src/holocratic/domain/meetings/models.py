"""Meeting domain entities including agenda and outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from holocratic.domain.base import (
    IdentifiedModel,
    JSONMetadataModel,
    StatusModel,
    TenantScopedModel,
    TimestampedModel,
)


class MeetingTemplate(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Reusable template describing a meeting structure."""

    __tablename__ = "meeting_templates"

    name: str = Field(sa_column=Column(String(length=200), nullable=False))
    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )
    cadence: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))

    meetings: list["MeetingInstance"] = Relationship(back_populates="template")


class MeetingInstance(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Individual meeting occurrence derived from a template."""

    __tablename__ = "meeting_instances"

    template_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("meeting_templates.id", ondelete="SET NULL"), index=True),
    )
    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )
    facilitator_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    scheduled_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)

    template: Optional[MeetingTemplate] = Relationship(back_populates="meetings")
    agenda_items: list["AgendaItem"] = Relationship(back_populates="meeting")
    outputs: list["MeetingOutput"] = Relationship(back_populates="meeting")
    checkins: list["MeetingCheckIn"] = Relationship(back_populates="meeting")


class AgendaItem(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Agenda items scheduled during a meeting."""

    __tablename__ = "agenda_items"

    meeting_id: UUID = Field(
        sa_column=Column(ForeignKey("meeting_instances.id", ondelete="CASCADE"), nullable=False),
    )
    title: str = Field(sa_column=Column(String(length=255), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String))
    order: int = Field(sa_column=Column(nullable=False))
    tension_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("tensions.id", ondelete="SET NULL"), index=True),
    )
    project_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("projects.id", ondelete="SET NULL"), index=True),
    )

    meeting: MeetingInstance = Relationship(back_populates="agenda_items")


class MeetingOutput(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Outputs captured from meetings."""

    __tablename__ = "meeting_outputs"

    meeting_id: UUID = Field(
        sa_column=Column(ForeignKey("meeting_instances.id", ondelete="CASCADE"), nullable=False),
    )
    notes: Optional[str] = Field(default=None, sa_column=Column(String))
    decisions: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )

    meeting: MeetingInstance = Relationship(back_populates="outputs")


class MeetingCheckIn(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    SQLModel,
    table=True,
):
    """Snapshot of partner check-in details for a meeting."""

    __tablename__ = "meeting_checkins"

    meeting_id: UUID = Field(
        sa_column=Column(ForeignKey("meeting_instances.id", ondelete="CASCADE"), nullable=False),
    )
    person_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    mood: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))
    highlights: Optional[str] = Field(default=None, sa_column=Column(String))
    blockers: Optional[str] = Field(default=None, sa_column=Column(String))

    meeting: MeetingInstance = Relationship(back_populates="checkins")


__all__ = [
    "MeetingTemplate",
    "MeetingInstance",
    "AgendaItem",
    "MeetingOutput",
    "MeetingCheckIn",
]
