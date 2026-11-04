# Employee Payroll Management System

A backend REST API for managing employee records and monthly payroll using **Python, FastAPI, PostgreSQL, SQLAlchemy, and Pydantic**.

## Features

### Employee Management
- Create new employee records.
- Retrieve all employees.
- Retrieve an employee by ID.
- Update employee information.
- Delete employee records.
- Prevent duplicate employee email addresses.

### Payroll Management
- Create monthly payroll records.
- Retrieve all payroll records.
- Retrieve payroll by ID.
- Retrieve payroll records for a specific employee.
- Filter payroll records by employee ID and month.
- Prevent duplicate payroll records for the same employee and month.
- Automatically calculate net salary.

### Payroll Calculation

Net salary is calculated using:

`Net Salary = Basic Salary + Bonus - Deductions`

The API validates salary values and prevents deductions from exceeding gross salary.

## Technology Stack

- Python 3.10+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Pydantic v2
- Uvicorn
- Pytest

## Project Structure

```text
PayrollManagement/
│
├── app/
│   ├── models/
│   │   ├── employee.py
│   │   └── payroll.py
│   │
│   ├── routers/
│   │   ├── employee.py
│   │   └── payroll.py
│   │
│   ├── schemas/
│   │   ├── employee.py
│   │   └── payroll.py
│   │
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── scripts/
│   └── create_db.py
│
├── tests/
│   └── test_payroll_api.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd PayrollManagement
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named:

```text
payroll_db
```

Create a `.env` file in the project root directory.

Example configuration:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=payroll_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

Replace the example password with your own PostgreSQL password.

**Important:** Never upload your actual `.env` file or database credentials to GitHub.

### 5. Initialize the database

```bash
python scripts/create_db.py
```

### 6. Run the application

```bash
python -m uvicorn app.main:app --reload --port 8001
```

## API Documentation

Once the application is running, open:

**Swagger UI:**

http://127.0.0.1:8001/docs

**ReDoc:**

http://127.0.0.1:8001/redoc

## API Endpoints

### Employee Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/employees` | Create an employee |
| GET | `/employees` | Retrieve all employees |
| GET | `/employees/{employee_id}` | Retrieve employee by ID |
| PUT | `/employees/{employee_id}` | Update employee |
| DELETE | `/employees/{employee_id}` | Delete employee |

### Payroll Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/payrolls` | Create monthly payroll |
| GET | `/payrolls` | Retrieve payroll records |
| GET | `/payrolls/{payroll_id}` | Retrieve payroll by ID |
| GET | `/payrolls/employee/{employee_id}` | Retrieve payroll by employee |

The payroll listing endpoint also supports filtering by employee ID and month, along with pagination.

## Example API Requests

### Create Employee

**POST** `/employees`

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "department": "IT",
  "designation": "Software Developer"
}
```

### Create Payroll

**POST** `/payrolls`

```json
{
  "employee_id": 1,
  "month": "2026-11",
  "basic_salary": 60000,
  "bonus": 5000,
  "deductions": 2500
}
```

Net salary:

```text
60000 + 5000 - 2500 = 62500
```

The employee ID must belong to an existing employee.

## Validation and Error Handling

The API includes validation for:

- Required employee information.
- Duplicate employee email addresses.
- Valid employee IDs.
- Valid payroll month format (`YYYY-MM`).
- Positive basic salary.
- Non-negative bonus and deductions.
- Deductions not exceeding gross salary.
- Duplicate payroll entries for the same employee and month.
- Missing employee and payroll records.

Appropriate HTTP status codes are returned for successful operations and errors.

## Database

The application uses PostgreSQL with SQLAlchemy ORM.

Main database tables:

- `employees`
- `payrolls`

Each payroll record is associated with an employee through a foreign key. A unique database constraint prevents duplicate payroll entries for the same employee and month.

## Running Tests

Run the test suite using:

```bash
pytest -v
```

**Latest confirmed test result: 22 passed.**

## Deployment

The project is intended for free-tier deployment using:

- **GitHub:** Source code hosting.
- **Neon:** Hosted PostgreSQL database.
- **Render:** FastAPI application hosting.

Deployment configuration will be added when the application is prepared for production.

## Future Improvements

- Authentication and authorization.
- Employee search and advanced filtering.
- Payroll reports and summaries.
- Frontend integration.
- Production deployment.

---

**Project:** Employee Payroll Management System  
**Type:** Backend REST API  
**Version:** 1.0.0