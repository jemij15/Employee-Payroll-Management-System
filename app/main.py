from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers.employee import router as employee_router
from app.routers.payroll import router as payroll_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Safely creates tables if they do not exist when the application starts.
    Does not drop or modify existing tables or data.
    """
    try:
        init_db()
        print("-> Database connected and tables verified/created successfully.")
    except Exception as e:
        print(f"-> Notice: Could not connect to database on startup: {e}")
        print("   Please check your .env configuration and ensure PostgreSQL is running.")
    yield


app = FastAPI(
    title="Employee Payroll Management System",
    description="A clean, beginner-friendly RESTful API for managing employees and monthly payrolls.",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI documentation
    redoc_url="/redoc",    # ReDoc documentation
    lifespan=lifespan,
)

# Enable CORS for local development / frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(employee_router)
app.include_router(payroll_router)


@app.get("/", tags=["Root"])
def root():
    """
    Welcome endpoint providing API status and link to interactive documentation.
    """
    return {
        "message": "Welcome to the Employee Payroll Management System API",
        "docs": "/docs",
        "status": "healthy",
        "endpoints": {
            "employees": "/employees",
            "payrolls": "/payrolls",
        },
    }


@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint for monitoring API status.
    """
    return {"status": "ok"}
