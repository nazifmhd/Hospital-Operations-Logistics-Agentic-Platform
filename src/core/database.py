"""
Database configuration and session management for the Hospital Operations Platform.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)

# Database URL construction
if settings.DATABASE_URL.startswith("sqlite"):
    # For SQLite, use synchronous connection
    DATABASE_URL = settings.DATABASE_URL
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    # For PostgreSQL and other databases
    DATABASE_URL = settings.DATABASE_URL
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create engines
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=StaticPool if "sqlite" in ASYNC_DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {},
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager to get database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize the database - create tables if they don't exist.
    """
    try:
        # Import all models to ensure they are registered
        from .models import Base
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def check_db_health() -> bool:
    """
    Check database connectivity and health.
    """
    try:
        async with get_async_db() as db:
            # Try to execute a simple query
            result = await db.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def populate_sample_data():
    """
    Populate the database with sample data for development/testing.
    """
    try:
        from .models import Bed, Equipment, Staff, Supply, BedStatus, EquipmentStatus, StaffStatus, SupplyStatus
        from .crud import bed_crud, equipment_crud, staff_crud, supply_crud
        
        # Use synchronous session for sample data population
        db = SessionLocal()
        try:
            # Check if data already exists
            existing_beds = db.query(Bed).first()
            if existing_beds:
                logger.info("Sample data already exists, skipping population")
                return
            
            # Sample beds
            sample_beds = [
                {"id": "BED-001", "room_number": "101", "department": "ICU", "bed_type": "ICU", "floor": 1, "wing": "North"},
                {"id": "BED-002", "room_number": "102", "department": "ICU", "bed_type": "ICU", "floor": 1, "wing": "North"},
                {"id": "BED-003", "room_number": "201", "department": "Emergency", "bed_type": "Standard", "floor": 2, "wing": "South"},
                {"id": "BED-004", "room_number": "202", "department": "Emergency", "bed_type": "Standard", "floor": 2, "wing": "South"},
                {"id": "BED-005", "room_number": "301", "department": "Surgery", "bed_type": "Recovery", "floor": 3, "wing": "East"},
            ]
            
            # Sample equipment
            sample_equipment = [
                {"id": "EQ-001", "name": "Ventilator", "equipment_type": "Life Support", "department": "ICU", "location": "ICU-01", "manufacturer": "Medtronic"},
                {"id": "EQ-002", "name": "X-Ray Machine", "equipment_type": "Imaging", "department": "Radiology", "location": "RAD-01", "manufacturer": "GE Healthcare"},
                {"id": "EQ-003", "name": "Defibrillator", "equipment_type": "Emergency", "department": "Emergency", "location": "ER-01", "manufacturer": "Philips"},
                {"id": "EQ-004", "name": "MRI Scanner", "equipment_type": "Imaging", "department": "Radiology", "location": "RAD-02", "manufacturer": "Siemens"},
                {"id": "EQ-005", "name": "Surgical Robot", "equipment_type": "Surgical", "department": "Surgery", "location": "OR-01", "manufacturer": "Da Vinci"},
            ]
            
            # Sample staff
            sample_staff = [
                {"id": "ST-001", "name": "Dr. Sarah Johnson", "role": "Doctor", "department": "ICU", "email": "sarah.johnson@hospital.com", "license_number": "MD12345"},
                {"id": "ST-002", "name": "Nurse Emily Davis", "role": "Nurse", "department": "ICU", "email": "emily.davis@hospital.com", "license_number": "RN67890"},
                {"id": "ST-003", "name": "Dr. Michael Chen", "role": "Doctor", "department": "Emergency", "email": "michael.chen@hospital.com", "license_number": "MD54321"},
                {"id": "ST-004", "name": "Tech Alex Rodriguez", "role": "Technician", "department": "Radiology", "email": "alex.rodriguez@hospital.com"},
                {"id": "ST-005", "name": "Dr. Lisa Thompson", "role": "Surgeon", "department": "Surgery", "email": "lisa.thompson@hospital.com", "license_number": "MD98765"},
            ]
            
            # Sample supplies
            sample_supplies = [
                {"id": "SUP-001", "name": "Surgical Gloves", "category": "PPE", "current_stock": 500, "minimum_threshold": 100, "maximum_capacity": 1000, "unit_cost": 0.50, "location": "Storage-A"},
                {"id": "SUP-002", "name": "Face Masks", "category": "PPE", "current_stock": 200, "minimum_threshold": 50, "maximum_capacity": 500, "unit_cost": 0.25, "location": "Storage-A"},
                {"id": "SUP-003", "name": "Syringes", "category": "Medical Devices", "current_stock": 150, "minimum_threshold": 30, "maximum_capacity": 300, "unit_cost": 1.50, "location": "Storage-B"},
                {"id": "SUP-004", "name": "Bandages", "category": "Consumables", "current_stock": 80, "minimum_threshold": 20, "maximum_capacity": 200, "unit_cost": 2.00, "location": "Storage-C"},
                {"id": "SUP-005", "name": "IV Bags", "category": "Medical Devices", "current_stock": 25, "minimum_threshold": 40, "maximum_capacity": 100, "unit_cost": 5.00, "location": "Pharmacy"},
            ]
            
            # Create sample data
            for bed_data in sample_beds:
                bed_crud.create(db, obj_in=bed_data)
            
            for equipment_data in sample_equipment:
                equipment_crud.create(db, obj_in=equipment_data)
            
            for staff_data in sample_staff:
                staff_crud.create(db, obj_in=staff_data)
            
            for supply_data in sample_supplies:
                supply_crud.create(db, obj_in=supply_data)
            
        finally:
            db.close()
        
        logger.info("Sample data populated successfully")
        
    except Exception as e:
        logger.error(f"Failed to populate sample data: {e}")
        raise


class DatabaseManager:
    """
    Database manager for handling connections and operations.
    """
    
    def __init__(self):
        self.engine = engine
        self.async_engine = async_engine
    
    async def create_tables(self):
        """Create all database tables."""
        await init_db()
    
    async def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        try:
            from .models import Base
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("All tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    async def reset_database(self):
        """Reset database - drop and recreate all tables."""
        await self.drop_tables()
        await self.create_tables()
        await populate_sample_data()
        logger.info("Database reset completed")
    
    async def health_check(self) -> dict:
        """Perform comprehensive database health check."""
        health_status = {
            "database": "unknown",
            "connectivity": False,
            "tables_exist": False,
            "last_check": datetime.utcnow().isoformat()
        }
        
        try:
            # Check connectivity
            health_status["connectivity"] = await check_db_health()
            
            # Check if tables exist
            if health_status["connectivity"]:
                async with self.async_engine.begin() as conn:
                    from .models import Base
                    
                    # Check if any tables exist
                    result = await conn.execute(text(
                        "SELECT name FROM sqlite_master WHERE type='table';" if "sqlite" in str(conn.engine.url)
                        else "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
                    ))
                    tables = result.fetchall()
                    health_status["tables_exist"] = len(tables) > 0
            
            health_status["database"] = "healthy" if health_status["connectivity"] and health_status["tables_exist"] else "unhealthy"
            
        except Exception as e:
            logger.error(f"Database health check error: {e}")
            health_status["database"] = "error"
            health_status["error"] = str(e)
        
        return health_status
