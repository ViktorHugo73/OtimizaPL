from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base

from sqlalchemy import JSON


def agora_utc():
    return datetime.now(timezone.utc)


class Problem(Base):

    __tablename__ = "problems"

    __table_args__ = (
        CheckConstraint(
            "objective_type IN ('min', 'max')",
            name="ck_problem_objective_type",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    objective_type: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=agora_utc,
        nullable=False,
    )

    variables = relationship(
        "Variable",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="Variable.id",
    )

    constraints = relationship(
        "Constraint",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="Constraint.id",
    )

    executions = relationship(
        "Execution",
        back_populates="problem",
        cascade="all, delete-orphan",
    )

    scenarios = relationship(
        "Scenario",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="Scenario.created_at",
    )


class Variable(Base):

    __tablename__ = "variables"

    __table_args__ = (
        UniqueConstraint(
            "problem_id",
            "name",
            name="uq_problem_variable_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey(
            "problems.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    objective_coefficient: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    lower_bound: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    upper_bound: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    problem = relationship(
        "Problem",
        back_populates="variables",
    )

    coefficients = relationship(
        "ConstraintCoefficient",
        back_populates="variable",
        cascade="all, delete-orphan",
    )

    results = relationship(
        "ResultVariable",
        back_populates="variable",
    )


class Constraint(Base):

    __tablename__ = "constraints"

    __table_args__ = (
        CheckConstraint(
            "operator IN ('<=', '>=', '=')",
            name="ck_constraint_operator",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey(
            "problems.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    rhs: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    problem = relationship(
        "Problem",
        back_populates="constraints",
    )

    coefficients = relationship(
        "ConstraintCoefficient",
        back_populates="constraint",
        cascade="all, delete-orphan",
    )


class ConstraintCoefficient(Base):

    __tablename__ = "constraint_coefficients"

    constraint_id: Mapped[int] = mapped_column(
        ForeignKey(
            "constraints.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    variable_id: Mapped[int] = mapped_column(
        ForeignKey(
            "variables.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    coefficient: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    constraint = relationship(
        "Constraint",
        back_populates="coefficients",
    )

    variable = relationship(
        "Variable",
        back_populates="coefficients",
    )

class Scenario(Base):

    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey(
            "problems.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    model_snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=agora_utc,
        nullable=False,
    )

    problem = relationship(
        "Problem",
        back_populates="scenarios",
    )

    executions = relationship(
        "Execution",
        back_populates="scenario",
    )

class Execution(Base):

    analysis_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey(
            "problems.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    objective_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    iterations_phase1: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    iterations_phase2: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    solver_version: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=agora_utc,
        nullable=False,
    )

    problem = relationship(
        "Problem",
        back_populates="executions",
    )

    variable_results = relationship(
        "ResultVariable",
        back_populates="execution",
        cascade="all, delete-orphan",
    )

    scenario_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "scenarios.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    scenario = relationship(
        "Scenario",
        back_populates="executions",
    )




class ResultVariable(Base):

    __tablename__ = "result_variables"

    execution_id: Mapped[int] = mapped_column(
        ForeignKey(
            "executions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    variable_id: Mapped[int] = mapped_column(
        ForeignKey(
            "variables.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    execution = relationship(
        "Execution",
        back_populates="variable_results",
    )

    variable = relationship(
        "Variable",
        back_populates="results",
    )