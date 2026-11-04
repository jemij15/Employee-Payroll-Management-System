
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PayrollBase(BaseModel):
    employee_id: int = Field(
        ...,
        gt=0,
        description="ID of the employee (must be greater than 0)"
    )

    month: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description="Payroll month in YYYY-MM format, e.g. 2026-11"
    )

    basic_salary: float = Field(
        ...,
        gt=0,
        description="Base salary (must be greater than 0)"
    )

    bonus: float = Field(
        default=0.0,
        ge=0,
        description="Bonus amount (must be greater than or equal to 0)"
    )

    deductions: float = Field(
        default=0.0,
        ge=0,
        description="Deductions amount (must be greater than or equal to 0)"
    )


class PayrollCreate(PayrollBase):

    @model_validator(mode="after")
    def validate_deductions_not_exceeding_gross(self):
        gross_salary = self.basic_salary + self.bonus

        if self.deductions > gross_salary:
            raise ValueError(
                "Deductions cannot exceed gross salary "
                f"(basic salary {self.basic_salary} + "
                f"bonus {self.bonus} = {gross_salary})"
            )

        return self


class PayrollResponse(PayrollBase):
    id: int

    net_salary: float = Field(
        ...,
        description="Calculated net salary: basic_salary + bonus - deductions"
    )

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
