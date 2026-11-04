from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Payroll(Base):
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String(20), nullable=False)   # Format: YYYY-MM, e.g. 2026-11
    basic_salary = Column(Float, nullable=False)
    bonus = Column(Float, nullable=False, default=0.0)
    deductions = Column(Float, nullable=False, default=0.0)
    net_salary = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to Employee
    employee = relationship("Employee", back_populates="payrolls")

    # Enforce uniqueness of employee and month combination
    __table_args__ = (
        UniqueConstraint("employee_id", "month", name="uq_employee_month"),
    )
