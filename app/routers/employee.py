from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new employee",
    description="Create a new employee record with personal and job details.",
)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    # Check if email is already registered
    existing_employee = db.query(Employee).filter(Employee.email == employee_in.email).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An employee with email '{employee_in.email}' already exists.",
        )

    employee = Employee(
        first_name=employee_in.first_name,
        last_name=employee_in.last_name,
        email=employee_in.email,
        department=employee_in.department,
        designation=employee_in.designation,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get(
    "",
    response_model=List[EmployeeResponse],
    status_code=status.HTTP_200_OK,
    summary="View all employees",
    description="Retrieve a list of all employees in the system.",
)
def get_all_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="View one employee by ID",
    description="Retrieve details of a single employee by their unique ID.",
)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )
    return employee


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update employee details",
    description="Update an employee's details by their ID. Only provided fields will be updated.",
)
def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    # If updating email, check for uniqueness conflict
    if employee_in.email and employee_in.email != employee.email:
        email_conflict = db.query(Employee).filter(
            Employee.email == employee_in.email,
            Employee.id != employee_id,
        ).first()
        if email_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An employee with email '{employee_in.email}' already exists.",
            )

    # Update only fields that were passed
    update_data = employee_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an employee",
    description="Delete an employee and their associated payroll records by ID.",
)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    db.delete(employee)
    db.commit()
    return {"message": f"Employee with ID {employee_id} deleted successfully."}
