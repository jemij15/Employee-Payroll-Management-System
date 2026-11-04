from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Employee's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Employee's last name")
    email: str = Field(..., min_length=3, max_length=150, description="Employee's unique email address")
    department: str = Field(..., min_length=1, max_length=100, description="Department name (e.g., Engineering, HR)")
    designation: str = Field(..., min_length=1, max_length=100, description="Job title / designation")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=3, max_length=150)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    designation: Optional[str] = Field(None, min_length=1, max_length=100)


class EmployeeResponse(EmployeeBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
