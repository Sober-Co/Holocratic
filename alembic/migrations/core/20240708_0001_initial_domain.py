"""Initial domain models."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = "20240708_0001"
down_revision = None
branch_labels = ("core",)
depends_on = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )
    op.create_index("ix_organizations_status", "organizations", ["status"])

    op.create_table(
        "circles",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("purpose", sa.String(length=500), nullable=True),
        sa.Column("parent_circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_circles_org_id", "circles", ["org_id"])
    op.create_index("ix_circles_status", "circles", ["status"])
    op.create_index("ix_circles_parent_circle_id", "circles", ["parent_circle_id"])

    op.create_table(
        "people",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_people_org_id", "people", ["org_id"])
    op.create_index("ix_people_status", "people", ["status"])
    op.create_index("ix_people_email_org", "people", ["org_id", "email"], unique=True)

    op.create_table(
        "policies",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("tags", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.create_index("ix_policies_org_id", "policies", ["org_id"])
    op.create_index("ix_policies_status", "policies", ["status"])
    op.create_index("ix_policies_circle_id", "policies", ["circle_id"])

    op.create_table(
        "meeting_templates",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cadence", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_meeting_templates_org_id", "meeting_templates", ["org_id"])
    op.create_index("ix_meeting_templates_status", "meeting_templates", ["status"])
    op.create_index("ix_meeting_templates_circle_id", "meeting_templates", ["circle_id"])

    op.create_table(
        "projects",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_projects_org_id", "projects", ["org_id"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_circle_id", "projects", ["circle_id"])
    op.create_index("ix_projects_lead_id", "projects", ["lead_id"])

    op.create_table(
        "roles",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("purpose", sa.String(length=500), nullable=True),
        sa.Column("accountabilities", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("domains", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metrics_config", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_roles_org_id", "roles", ["org_id"])
    op.create_index("ix_roles_status", "roles", ["status"])
    op.create_index("ix_roles_circle_id", "roles", ["circle_id"])

    op.create_table(
        "metrics",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role_id", pg.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("target", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("cadence", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_metrics_org_id", "metrics", ["org_id"])
    op.create_index("ix_metrics_status", "metrics", ["status"])
    op.create_index("ix_metrics_circle_id", "metrics", ["circle_id"])
    op.create_index("ix_metrics_role_id", "metrics", ["role_id"])

    op.create_table(
        "meeting_instances",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("template_id", pg.UUID(as_uuid=True), sa.ForeignKey("meeting_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("facilitator_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_meeting_instances_org_id", "meeting_instances", ["org_id"])
    op.create_index("ix_meeting_instances_status", "meeting_instances", ["status"])
    op.create_index("ix_meeting_instances_circle_id", "meeting_instances", ["circle_id"])

    op.create_table(
        "objectives",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("owner_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timeframe", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_objectives_org_id", "objectives", ["org_id"])
    op.create_index("ix_objectives_status", "objectives", ["status"])
    op.create_index("ix_objectives_owner_id", "objectives", ["owner_id"])

    op.create_table(
        "tensions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("raised_by_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("circle_id", pg.UUID(as_uuid=True), sa.ForeignKey("circles.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_tensions_org_id", "tensions", ["org_id"])
    op.create_index("ix_tensions_status", "tensions", ["status"])
    op.create_index("ix_tensions_circle_id", "tensions", ["circle_id"])

    op.create_table(
        "tasks",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("project_id", pg.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignee_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tasks_org_id", "tasks", ["org_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    op.create_index("ix_tasks_assignee_id", "tasks", ["assignee_id"])

    op.create_table(
        "agenda_items",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("meeting_id", pg.UUID(as_uuid=True), sa.ForeignKey("meeting_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("tension_id", pg.UUID(as_uuid=True), sa.ForeignKey("tensions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("project_id", pg.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_agenda_items_org_id", "agenda_items", ["org_id"])
    op.create_index("ix_agenda_items_status", "agenda_items", ["status"])
    op.create_index("ix_agenda_items_meeting_id", "agenda_items", ["meeting_id"])
    op.create_index("ix_agenda_items_tension_id", "agenda_items", ["tension_id"])
    op.create_index("ix_agenda_items_project_id", "agenda_items", ["project_id"])

    op.create_table(
        "governance_proposals",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("tension_id", pg.UUID(as_uuid=True), sa.ForeignKey("tensions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("proposer_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("payload_type", sa.String(length=50), nullable=False),
    )
    op.create_index("ix_governance_proposals_org_id", "governance_proposals", ["org_id"])
    op.create_index("ix_governance_proposals_status", "governance_proposals", ["status"])
    op.create_index("ix_governance_proposals_tension_id", "governance_proposals", ["tension_id"])
    op.create_index("ix_governance_proposals_proposer_id", "governance_proposals", ["proposer_id"])

    op.create_table(
        "meeting_outputs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("meeting_id", pg.UUID(as_uuid=True), sa.ForeignKey("meeting_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("decisions", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.create_index("ix_meeting_outputs_org_id", "meeting_outputs", ["org_id"])
    op.create_index("ix_meeting_outputs_status", "meeting_outputs", ["status"])
    op.create_index("ix_meeting_outputs_meeting_id", "meeting_outputs", ["meeting_id"])

    op.create_table(
        "okr_alignments",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("parent_objective_id", pg.UUID(as_uuid=True), sa.ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False),
        sa.Column("child_objective_id", pg.UUID(as_uuid=True), sa.ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alignment_type", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_okr_alignments_org_id", "okr_alignments", ["org_id"])
    op.create_index("ix_okr_alignments_status", "okr_alignments", ["status"])
    op.create_index("ix_okr_alignments_parent_child", "okr_alignments", ["parent_objective_id", "child_objective_id"], unique=True)

    op.create_table(
        "role_assignments",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("role_id", pg.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("person_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vacated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_role_assignments_org_id", "role_assignments", ["org_id"])
    op.create_index("ix_role_assignments_status", "role_assignments", ["status"])
    op.create_index("ix_role_assignments_role_id", "role_assignments", ["role_id"])
    op.create_index("ix_role_assignments_person_id", "role_assignments", ["person_id"])

    op.create_table(
        "governance_proposal_payloads",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("proposal_id", pg.UUID(as_uuid=True), sa.ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payload_type", sa.String(length=50), nullable=False),
        sa.Column("payload", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_governance_proposal_payloads_org_id", "governance_proposal_payloads", ["org_id"])
    op.create_index("ix_governance_proposal_payloads_status", "governance_proposal_payloads", ["status"])
    op.create_index(
        "ix_governance_proposal_payloads_proposal_id",
        "governance_proposal_payloads",
        ["proposal_id"],
    )

    op.create_table(
        "governance_records",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("proposal_id", pg.UUID(as_uuid=True), sa.ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.String(), nullable=False),
    )
    op.create_index("ix_governance_records_org_id", "governance_records", ["org_id"])
    op.create_index("ix_governance_records_status", "governance_records", ["status"])
    op.create_index("ix_governance_records_proposal_id", "governance_records", ["proposal_id"])

    op.create_table(
        "meeting_checkins",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("meeting_id", pg.UUID(as_uuid=True), sa.ForeignKey("meeting_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("person_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("mood", sa.String(length=50), nullable=True),
        sa.Column("highlights", sa.String(), nullable=True),
        sa.Column("blockers", sa.String(), nullable=True),
    )
    op.create_index("ix_meeting_checkins_org_id", "meeting_checkins", ["org_id"])
    op.create_index("ix_meeting_checkins_status", "meeting_checkins", ["status"])
    op.create_index("ix_meeting_checkins_meeting_id", "meeting_checkins", ["meeting_id"])
    op.create_index("ix_meeting_checkins_person_id", "meeting_checkins", ["person_id"])

    op.create_table(
        "objections",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("proposal_id", pg.UUID(as_uuid=True), sa.ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raised_by_id", pg.UUID(as_uuid=True), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rationale", sa.String(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_objections_org_id", "objections", ["org_id"])
    op.create_index("ix_objections_status", "objections", ["status"])
    op.create_index("ix_objections_proposal_id", "objections", ["proposal_id"])

    op.create_table(
        "checklist_items",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("task_id", pg.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_checklist_items_org_id", "checklist_items", ["org_id"])
    op.create_index("ix_checklist_items_status", "checklist_items", ["status"])
    op.create_index("ix_checklist_items_task_id", "checklist_items", ["task_id"])

    op.create_table(
        "key_results",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        *_timestamp_columns(),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("properties", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("objective_id", pg.UUID(as_uuid=True), sa.ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_id", pg.UUID(as_uuid=True), sa.ForeignKey("metrics.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("current_value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_key_results_org_id", "key_results", ["org_id"])
    op.create_index("ix_key_results_status", "key_results", ["status"])
    op.create_index("ix_key_results_objective_id", "key_results", ["objective_id"])


def downgrade() -> None:
    raise RuntimeError("Downgrade is not supported for the initial migration")
