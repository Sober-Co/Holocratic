"""Core organization structure models."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
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


class Organization(IdentifiedModel, TimestampedModel, StatusModel, JSONMetadataModel, SQLModel, table=True):
    """Represents a tenant organization within the system."""

    __tablename__ = "organizations"

    name: str = Field(sa_column=Column(String(length=200), nullable=False))
    slug: str = Field(sa_column=Column(String(length=120), nullable=False, unique=True))

    circles: List["Circle"] = Relationship(back_populates="organization")
    people: List["Person"] = Relationship(back_populates="organization")


class Circle(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Represents a holocratic circle grouping roles."""

    __tablename__ = "circles"

    name: str = Field(sa_column=Column(String(length=200), nullable=False))
    purpose: Optional[str] = Field(default=None, sa_column=Column(String(length=500)))
    parent_circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )

    organization: Organization = Relationship(back_populates="circles")
    parent_circle: Optional["Circle"] = Relationship(back_populates="child_circles", sa_relationship_kwargs={"remote_side": "Circle.id"})
    child_circles: List["Circle"] = Relationship(back_populates="parent_circle")
    roles: List["Role"] = Relationship(back_populates="circle")
    policies: List["Policy"] = Relationship(back_populates="circle")
    metrics: List["Metric"] = Relationship(back_populates="circle")


class Person(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Person belonging to an organization."""

    __tablename__ = "people"

    first_name: str = Field(sa_column=Column(String(length=120), nullable=False))
    last_name: str = Field(sa_column=Column(String(length=120), nullable=False))
    email: str = Field(sa_column=Column(String(length=255), nullable=False))

    organization: Organization = Relationship(back_populates="people")
    assignments: List["RoleAssignment"] = Relationship(back_populates="person")


class Role(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Roles capture accountability within circles."""

    __tablename__ = "roles"

    circle_id: UUID = Field(sa_column=Column(ForeignKey("circles.id", ondelete="CASCADE"), nullable=False, index=True))
    name: str = Field(sa_column=Column(String(length=200), nullable=False))
    purpose: Optional[str] = Field(default=None, sa_column=Column(String(length=500)))
    accountabilities: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    domains: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    metrics_config: dict | None = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="{}"),
    )

    circle: Circle = Relationship(back_populates="roles")
    assignments: List["RoleAssignment"] = Relationship(back_populates="role")
    metrics: List["Metric"] = Relationship(back_populates="role")


class RoleAssignment(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    SQLModel,
    table=True,
):
    """Assignment of a person to a role."""

    __tablename__ = "role_assignments"

    role_id: UUID = Field(sa_column=Column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False))
    person_id: UUID = Field(sa_column=Column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False))
    assigned_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    vacated_at: Optional[datetime] = Field(default=None)

    role: Role = Relationship(back_populates="assignments")
    person: Person = Relationship(back_populates="assignments")


class Policy(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Explicit policies recorded within circles."""

    __tablename__ = "policies"

    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )
    title: str = Field(sa_column=Column(String(length=255), nullable=False))
    content: str = Field(sa_column=Column(String, nullable=False))
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )

    circle: Optional[Circle] = Relationship(back_populates="policies")


class Metric(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Key metrics tracked for roles or circles."""

    __tablename__ = "metrics"

    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )
    role_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("roles.id", ondelete="SET NULL"), index=True),
    )
    name: str = Field(sa_column=Column(String(length=200), nullable=False))
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(String(length=500)),
    )
    target: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))
    cadence: Optional[str] = Field(default=None, sa_column=Column(String(length=50)))

    circle: Optional[Circle] = Relationship(back_populates="metrics")
    role: Optional[Role] = Relationship(back_populates="metrics")


__all__ = [
    "Organization",
    "Circle",
    "Role",
    "RoleAssignment",
    "Person",
    "Policy",
    "Metric",
]
