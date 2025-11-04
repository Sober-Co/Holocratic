"""Work management and OKR entities."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel

from holocratic.domain.base import (
    IdentifiedModel,
    JSONMetadataModel,
    StatusModel,
    TenantScopedModel,
    TimestampedModel,
)


class Project(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Project grouping tasks and checklists."""

    __tablename__ = "projects"

    name: str = Field(sa_column=Column(String(length=200), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String))
    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )
    lead_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    due_date: Optional[date] = Field(default=None)

    tasks: list["Task"] = Relationship(back_populates="project")


class Task(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Task associated with a project."""

    __tablename__ = "tasks"

    project_id: UUID = Field(
        sa_column=Column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
    )
    assignee_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    title: str = Field(sa_column=Column(String(length=255), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String))
    due_date: Optional[date] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    project: Project = Relationship(back_populates="tasks")
    checklist_items: list["ChecklistItem"] = Relationship(back_populates="task")


class ChecklistItem(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    SQLModel,
    table=True,
):
    """Checklist item within a task."""

    __tablename__ = "checklist_items"

    task_id: UUID = Field(
        sa_column=Column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
    )
    title: str = Field(sa_column=Column(String(length=200), nullable=False))
    is_completed: bool = Field(default=False, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    task: Task = Relationship(back_populates="checklist_items")


class Objective(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Objective forming part of OKR planning."""

    __tablename__ = "objectives"

    title: str = Field(sa_column=Column(String(length=255), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String))
    owner_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )
    timeframe: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))

    key_results: list["KeyResult"] = Relationship(back_populates="objective")
    alignments_from: list["OKRAlignment"] = Relationship(
        back_populates="child_objective",
        sa_relationship_kwargs={"foreign_keys": "OKRAlignment.child_objective_id"},
    )
    alignments_to: list["OKRAlignment"] = Relationship(
        back_populates="parent_objective",
        sa_relationship_kwargs={"foreign_keys": "OKRAlignment.parent_objective_id"},
    )


class KeyResult(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Key results quantify objective progress."""

    __tablename__ = "key_results"

    objective_id: UUID = Field(
        sa_column=Column(ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False),
    )
    metric_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("metrics.id", ondelete="SET NULL"), index=True),
    )
    title: str = Field(sa_column=Column(String(length=255), nullable=False))
    target_value: Optional[float] = Field(default=None)
    current_value: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))

    objective: Objective = Relationship(back_populates="key_results")


class OKRAlignment(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    SQLModel,
    table=True,
):
    """Alignment table mapping related objectives."""

    __tablename__ = "okr_alignments"

    parent_objective_id: UUID = Field(
        sa_column=Column(ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False),
    )
    child_objective_id: UUID = Field(
        sa_column=Column(ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False),
    )
    alignment_type: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))

    parent_objective: Objective = Relationship(
        back_populates="alignments_to",
        sa_relationship_kwargs={"foreign_keys": "OKRAlignment.parent_objective_id"},
    )
    child_objective: Objective = Relationship(
        back_populates="alignments_from",
        sa_relationship_kwargs={"foreign_keys": "OKRAlignment.child_objective_id"},
    )


__all__ = [
    "Project",
    "Task",
    "ChecklistItem",
    "Objective",
    "KeyResult",
    "OKRAlignment",
]
