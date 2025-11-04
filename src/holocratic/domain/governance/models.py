"""Governance domain models for the holocratic process."""

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


class Tension(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Represents sensed tensions raised by partners."""

    __tablename__ = "tensions"

    title: str = Field(sa_column=Column(String(length=255), nullable=False))
    description: str = Field(sa_column=Column(String, nullable=False))
    raised_by_id: UUID = Field(sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), nullable=True))
    circle_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("circles.id", ondelete="SET NULL"), index=True),
    )

    proposals: list["GovernanceProposal"] = Relationship(back_populates="tension")


class GovernanceProposal(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Governance proposal generated to resolve a tension."""

    __tablename__ = "governance_proposals"

    tension_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("tensions.id", ondelete="SET NULL"), index=True),
    )
    proposer_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    summary: str = Field(sa_column=Column(String(length=255), nullable=False))
    payload_type: str = Field(sa_column=Column(String(length=50), nullable=False))
    payload: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default="{}"),
    )

    tension: Optional[Tension] = Relationship(back_populates="proposals")
    objections: list["Objection"] = Relationship(back_populates="proposal")
    records: list["GovernanceRecord"] = Relationship(back_populates="proposal")
    payloads: list["ProposalPayloadBase"] = Relationship(back_populates="proposal")


class Objection(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    SQLModel,
    table=True,
):
    """Objection captured during governance processing."""

    __tablename__ = "objections"

    proposal_id: UUID = Field(sa_column=Column(ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False))
    raised_by_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("people.id", ondelete="SET NULL"), index=True),
    )
    rationale: str = Field(sa_column=Column(String, nullable=False))
    resolved_at: Optional[datetime] = Field(default=None)

    proposal: GovernanceProposal = Relationship(back_populates="objections")


class GovernanceRecord(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    StatusModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Timeline records for governance decisions."""

    __tablename__ = "governance_records"

    proposal_id: UUID = Field(
        sa_column=Column(ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False),
    )
    recorded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    notes: str = Field(sa_column=Column(String, nullable=False))

    proposal: GovernanceProposal = Relationship(back_populates="records")


class ProposalPayloadBase(
    IdentifiedModel,
    TenantScopedModel,
    TimestampedModel,
    JSONMetadataModel,
    SQLModel,
    table=True,
):
    """Polymorphic base storing proposal payloads."""

    __tablename__ = "governance_proposal_payloads"
    __mapper_args__ = {"polymorphic_on": "payload_type", "polymorphic_identity": "base"}

    proposal_id: UUID = Field(
        sa_column=Column(ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False),
    )
    payload_type: str = Field(sa_column=Column(String(length=50), nullable=False))

    proposal: GovernanceProposal = Relationship(back_populates="payloads")


class RoleChange(ProposalPayloadBase, table=False):
    """Role change payload for proposals."""

    __mapper_args__ = {"polymorphic_identity": "role_change"}


class PolicyChange(ProposalPayloadBase, table=False):
    """Policy change payload for proposals."""

    __mapper_args__ = {"polymorphic_identity": "policy_change"}


class CircleChange(ProposalPayloadBase, table=False):
    """Circle change payload for proposals."""

    __mapper_args__ = {"polymorphic_identity": "circle_change"}


class ProposalCreated(SQLModel):
    """Domain event emitted when a proposal is created."""

    proposal_id: UUID
    org_id: UUID
    created_at: datetime


class ProposalResolved(SQLModel):
    """Domain event emitted when a proposal is resolved."""

    proposal_id: UUID
    org_id: UUID
    resolved_at: datetime
    outcome: str


__all__ = [
    "Tension",
    "GovernanceProposal",
    "Objection",
    "GovernanceRecord",
    "ProposalPayloadBase",
    "RoleChange",
    "PolicyChange",
    "CircleChange",
    "ProposalCreated",
    "ProposalResolved",
]
