from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.models.payroll import Payroll
from app.schemas.payroll import PayrollCreate, PayrollResponse

router = APIRouter(
    prefix="/payrolls",
    tags=["Payrolls"],
)


@router.post(
    "",
    response_model=PayrollResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate monthly payroll for an employee",
    description="Calculate net salary and record payroll. Prevents duplicate entries for the same employee and month.",
)
def generate_payroll(payroll_in: PayrollCreate, db: Session = Depends(get_db)):
    # 1. Verify that the employee exists
    employee = db.query(Employee).filter(Employee.id == payroll_in.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {payroll_in.employee_id} not found.",
        )

    # 2. Check for duplicate payroll entry for the same employee and month
    duplicate = (
        db.query(Payroll)
        .filter(
            Payroll.employee_id == payroll_in.employee_id,
            Payroll.month == payroll_in.month,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payroll for employee ID {payroll_in.employee_id} for month '{payroll_in.month}' already exists.",
        )

    # 3. Calculate net salary = basic_salary + bonus - deductions
    calculated_net_salary = round(
        payroll_in.basic_salary + payroll_in.bonus - payroll_in.deductions, 2
    )

    # 4. Create and persist payroll record
    payroll = Payroll(
        employee_id=payroll_in.employee_id,
        month=payroll_in.month,
        basic_salary=payroll_in.basic_salary,
        bonus=payroll_in.bonus,
        deductions=payroll_in.deductions,
        net_salary=calculated_net_salary,
    )
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return payroll


@router.get(
    "",
    response_model=List[PayrollResponse],
    status_code=status.HTTP_200_OK,
    summary="View payroll history",
    description="Retrieve payroll records. Can optionally be filtered by employee ID or month.",
)
def get_payroll_history(
    employee_id: Optional[int] = Query(None, description="Filter history by Employee ID"),
    month: Optional[str] = Query(None, description="Filter history by Month (e.g. '2026-11')"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Payroll)
    if employee_id is not None:
        query = query.filter(Payroll.employee_id == employee_id)
    if month is not None:
        query = query.filter(Payroll.month == month)

    payrolls = query.order_by(Payroll.id.desc()).offset(skip).limit(limit).all()
    return payrolls


@router.get(
    "/{payroll_id}",
    response_model=PayrollResponse,
    status_code=status.HTTP_200_OK,
    summary="View one payroll record by ID",
    description="Retrieve details of a specific payroll entry.",
)
def get_payroll_by_id(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payroll record with ID {payroll_id} not found.",
        )
    return payroll


@router.get(
    "/employee/{employee_id}",
    response_model=List[PayrollResponse],
    status_code=status.HTTP_200_OK,
    summary="View payroll history for a specific employee",
    description="Retrieve all payroll records generated for a specific employee ID.",
)
def get_payrolls_by_employee_id(employee_id: int, db: Session = Depends(get_db)):
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    payrolls = (
        db.query(Payroll)
        .filter(Payroll.employee_id == employee_id)
        .order_by(Payroll.id.desc())
        .all()
    )
    return payrolls
