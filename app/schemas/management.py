from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MetadataUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class MetadataPatch(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None

    @field_validator('name')
    @classmethod
    def name_not_null(cls, value):
        if value is None:
            raise ValueError('Nome não pode ser nulo.')
        return value


class ProblemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    objective_type: str
    created_at: datetime
