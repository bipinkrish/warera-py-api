from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class WorkStats(BaseModel):
    """Daily work statistics for a user, company, or worker+company combination."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )

    daily_date: str | None = Field(
        default=None, validation_alias=AliasChoices("dailyDate", "daily_date")
    )
    total: float | None = None
    wage: float | None = None
    employee_prod: float | None = Field(
        default=None, validation_alias=AliasChoices("employeeProd", "employee_prod")
    )
    self_work: float | None = Field(
        default=None, validation_alias=AliasChoices("selfWork", "self_work")
    )
    automated_engine: float | None = Field(
        default=None, validation_alias=AliasChoices("automatedEngine", "automated_engine")
    )
