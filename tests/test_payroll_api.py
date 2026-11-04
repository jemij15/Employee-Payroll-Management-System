import os
# Set DATABASE_URL to in-memory SQLite before importing application modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db, engine
from app.main import app

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the get_db dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create a fresh schema before each test and drop it afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# Root and Documentation Tests
# ============================================================================
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "/docs" in data["docs"]


def test_swagger_docs():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text or "swagger" in response.text.lower()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ============================================================================
# 1. Employee Management Tests
# ============================================================================
def test_add_employee():
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "department": "Engineering",
        "designation": "Backend Developer",
    }
    response = client.post("/employees", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["first_name"] == "Alice"
    assert data["last_name"] == "Smith"
    assert data["email"] == "alice.smith@example.com"
    assert data["department"] == "Engineering"
    assert data["designation"] == "Backend Developer"
    assert "created_at" in data


def test_add_duplicate_employee_email():
    payload = {
        "first_name": "Bob",
        "last_name": "Brown",
        "email": "bob@example.com",
        "department": "Finance",
        "designation": "Analyst",
    }
    res1 = client.post("/employees", json=payload)
    assert res1.status_code == 201

    # Attempt to add same email
    res2 = client.post("/employees", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_view_all_employees():
    emp1 = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "department": "HR",
        "designation": "Manager",
    }
    emp2 = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "department": "Marketing",
        "designation": "Lead",
    }
    client.post("/employees", json=emp1)
    client.post("/employees", json=emp2)

    response = client.get("/employees")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_view_one_employee_by_id():
    payload = {
        "first_name": "Charlie",
        "last_name": "Green",
        "email": "charlie@example.com",
        "department": "IT",
        "designation": "DevOps Engineer",
    }
    created = client.post("/employees", json=payload).json()
    emp_id = created["id"]

    response = client.get(f"/employees/{emp_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == emp_id
    assert data["email"] == "charlie@example.com"


def test_view_nonexistent_employee():
    response = client.get("/employees/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_employee():
    payload = {
        "first_name": "David",
        "last_name": "White",
        "email": "david@example.com",
        "department": "Support",
        "designation": "Associate",
    }
    created = client.post("/employees", json=payload).json()
    emp_id = created["id"]

    update_payload = {
        "designation": "Senior Support Specialist",
        "department": "Customer Success",
    }
    response = client.put(f"/employees/{emp_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["designation"] == "Senior Support Specialist"
    assert data["department"] == "Customer Success"
    assert data["first_name"] == "David"  # Unchanged field remains intact


def test_delete_employee():
    payload = {
        "first_name": "Eve",
        "last_name": "Black",
        "email": "eve@example.com",
        "department": "Sales",
        "designation": "Executive",
    }
    created = client.post("/employees", json=payload).json()
    emp_id = created["id"]

    # Delete employee
    del_response = client.delete(f"/employees/{emp_id}")
    assert del_response.status_code == 200
    assert "deleted successfully" in del_response.json()["message"]

    # Ensure employee is no longer found
    get_response = client.get(f"/employees/{emp_id}")
    assert get_response.status_code == 404


# ============================================================================
# 2. Payroll Management Tests
# ============================================================================
def test_generate_payroll_and_calculation():
    # Create employee first
    emp = client.post(
        "/employees",
        json={
            "first_name": "Frank",
            "last_name": "Miller",
            "email": "frank@example.com",
            "department": "Engineering",
            "designation": "Software Engineer",
        },
    ).json()
    emp_id = emp["id"]

    payroll_data = {
        "employee_id": emp_id,
        "month": "2026-11",
        "basic_salary": 50000.0,
        "bonus": 7500.0,
        "deductions": 3000.0,
    }
    response = client.post("/payrolls", json=payroll_data)
    assert response.status_code == 201
    data = response.json()

    # Net salary formula check: 50000 + 7500 - 3000 = 54500
    assert data["basic_salary"] == 50000.0
    assert data["bonus"] == 7500.0
    assert data["deductions"] == 3000.0
    assert data["net_salary"] == 54500.0
    assert data["month"] == "2026-11"
    assert data["employee_id"] == emp_id


def test_prevent_duplicate_payroll_for_same_employee_and_month():
    emp = client.post(
        "/employees",
        json={
            "first_name": "Grace",
            "last_name": "Hopper",
            "email": "grace@example.com",
            "department": "R&D",
            "designation": "Scientist",
        },
    ).json()
    emp_id = emp["id"]

    payroll_payload = {
        "employee_id": emp_id,
        "month": "2026-11",
        "basic_salary": 60000.0,
        "bonus": 5000.0,
        "deductions": 2000.0,
    }
    # First payroll generation should succeed
    res1 = client.post("/payrolls", json=payroll_payload)
    assert res1.status_code == 201

    # Second payroll generation for the SAME employee and SAME month must fail
    res2 = client.post("/payrolls", json=payroll_payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_generate_payroll_different_months():
    emp = client.post(
        "/employees",
        json={
            "first_name": "Helen",
            "last_name": "Keller",
            "email": "helen@example.com",
            "department": "Education",
            "designation": "Instructor",
        },
    ).json()
    emp_id = emp["id"]

    # Month 1
    res1 = client.post(
        "/payrolls",
        json={
            "employee_id": emp_id,
            "month": "2026-10",
            "basic_salary": 45000.0,
            "bonus": 2000.0,
            "deductions": 1000.0,
        },
    )
    assert res1.status_code == 201

    # Month 2 (Different month for same employee should succeed)
    res2 = client.post(
        "/payrolls",
        json={
            "employee_id": emp_id,
            "month": "2026-11",
            "basic_salary": 45000.0,
            "bonus": 3000.0,
            "deductions": 1000.0,
        },
    )
    assert res2.status_code == 201


def test_generate_payroll_nonexistent_employee():
    payroll_payload = {
        "employee_id": 9999,
        "month": "2026-11",
        "basic_salary": 50000.0,
        "bonus": 1000.0,
        "deductions": 500.0,
    }
    response = client.post("/payrolls", json=payroll_payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_payroll_history_and_filters():
    # Setup two employees
    emp1 = client.post(
        "/employees",
        json={"first_name": "Ian", "last_name": "M", "email": "ian@example.com", "department": "QA", "designation": "Tester"},
    ).json()
    emp2 = client.post(
        "/employees",
        json={"first_name": "Joy", "last_name": "K", "email": "joy@example.com", "department": "UI", "designation": "Designer"},
    ).json()

    # Generate payrolls
    client.post("/payrolls", json={"employee_id": emp1["id"], "month": "2026-10", "basic_salary": 40000, "bonus": 0, "deductions": 0})
    client.post("/payrolls", json={"employee_id": emp1["id"], "month": "2026-11", "basic_salary": 40000, "bonus": 1000, "deductions": 500})
    client.post("/payrolls", json={"employee_id": emp2["id"], "month": "2026-11", "basic_salary": 48000, "bonus": 2000, "deductions": 1000})

    # 1. View all payroll history
    res_all = client.get("/payrolls")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    # 2. Filter by employee_id
    res_emp1 = client.get(f"/payrolls?employee_id={emp1['id']}")
    assert res_emp1.status_code == 200
    assert len(res_emp1.json()) == 2

    # 3. Filter by month
    res_month = client.get("/payrolls?month=2026-10")
    assert res_month.status_code == 200
    assert len(res_month.json()) == 1

    # 4. View by specific employee route
    res_emp_route = client.get(f"/payrolls/employee/{emp2['id']}")
    assert res_emp_route.status_code == 200
    assert len(res_emp_route.json()) == 1
    assert res_emp_route.json()[0]["net_salary"] == 49000.0


def test_view_one_payroll_by_id():
    emp = client.post(
        "/employees",
        json={"first_name": "Ken", "last_name": "L", "email": "ken@example.com", "department": "Ops", "designation": "Admin"},
    ).json()
    payroll = client.post(
        "/payrolls",
        json={"employee_id": emp["id"], "month": "2026-11", "basic_salary": 35000, "bonus": 1500, "deductions": 500},
    ).json()

    response = client.get(f"/payrolls/{payroll['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == payroll["id"]
    assert data["net_salary"] == 36000.0


def test_input_validation_deductions_exceed_gross():
    emp = client.post(
        "/employees",
        json={"first_name": "Leo", "last_name": "T", "email": "leo@example.com", "department": "Dev", "designation": "Junior"},
    ).json()

    # Deductions (60000) > basic (50000) + bonus (5000)
    invalid_payroll = {
        "employee_id": emp["id"],
        "month": "2026-11",
        "basic_salary": 50000.0,
        "bonus": 5000.0,
        "deductions": 60000.0,
    }
    response = client.post("/payrolls", json=invalid_payroll)
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "employee_id": 1,
            "month": "2026-99",
            "basic_salary": 30000,
            "bonus": 1000,
            "deductions": 500,
        },
        {
            "employee_id": 1,
            "month": "November 2026",
            "basic_salary": 30000,
            "bonus": 1000,
            "deductions": 500,
        },
        {
            "employee_id": 1,
            "month": "2026-11",
            "basic_salary": 0,
            "bonus": 1000,
            "deductions": 500,
        },
        {
            "employee_id": 1,
            "month": "2026-11",
            "basic_salary": 30000,
            "bonus": -100,
            "deductions": 500,
        },
        {
            "employee_id": 1,
            "month": "2026-11",
            "basic_salary": 30000,
            "bonus": 1000,
            "deductions": -100,
        },
    ],
)
def test_payroll_input_validation(invalid_data):
    response = client.post("/payrolls", json=invalid_data)

    assert response.status_code == 422