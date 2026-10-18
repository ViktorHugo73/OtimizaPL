from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


class VariableCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    objective_coefficient: float

    lower_bound: float = Field(
        default=0.0,
        ge=0.0,
    )

    upper_bound: float | None = None

    @model_validator(mode="after")
    def validar_limites(self):

        if (
            self.upper_bound is not None
            and
            self.upper_bound < self.lower_bound
        ):
            raise ValueError(
                "upper_bound não pode ser menor "
                "que lower_bound."
            )

        return self


class ConstraintTermCreate(BaseModel):

    variable_name: str

    coefficient: float


class ConstraintCreate(BaseModel):

    name: str

    operator: Literal[
        "<=",
        ">=",
        "=",
    ]

    rhs: float

    terms: list[
        ConstraintTermCreate
    ] = Field(
        min_length=1
    )


class ProblemCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    objective_type: Literal[
        "min",
        "max",
    ]

    variables: list[
        VariableCreate
    ] = Field(
        min_length=1
    )

    constraints: list[
        ConstraintCreate
    ] = Field(
        min_length=1
    )


class VariableRead(BaseModel):

    id: int

    name: str

    description: str | None

    objective_coefficient: float

    lower_bound: float

    upper_bound: float | None


class ConstraintTermRead(BaseModel):

    variable_id: int

    variable_name: str

    coefficient: float


class ConstraintRead(BaseModel):

    id: int

    name: str

    operator: str

    rhs: float

    terms: list[
        ConstraintTermRead
    ]


class ProblemRead(BaseModel):

    id: int

    name: str

    description: str | None

    objective_type: str

    variables: list[
        VariableRead
    ]

    constraints: list[
        ConstraintRead
    ]