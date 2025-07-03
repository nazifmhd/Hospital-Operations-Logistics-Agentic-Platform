"""
SQLAlchemy database models for the Hospital Operations & Logistics Platform.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class BedStatus(enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class EquipmentStatus(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"


class StaffStatus(enum.Enum):
    AVAILABLE = "available"
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    ON_BREAK = "on_break"


class SupplyStatus(enum.Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    EXPIRED = "expired"


class Bed(Base):
    __tablename__ = "beds"

    id = Column(String, primary_key=True)
    room_number = Column(String, nullable=False)
    department = Column(String, nullable=False)
    bed_type = Column(String, nullable=False)
    status = Column(Enum(BedStatus), nullable=False, default=BedStatus.AVAILABLE)
    patient_id = Column(String, nullable=True)
    last_cleaned = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    floor = Column(Integer, nullable=True)
    wing = Column(String, nullable=True)
    isolation_required = Column(Boolean, default=False)
    special_equipment = Column(Text, nullable=True)


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    department = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(Enum(EquipmentStatus), nullable=False, default=EquipmentStatus.AVAILABLE)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Operational data
    usage_hours = Column(Float, default=0.0)
    maintenance_cost = Column(Float, default=0.0)
    assigned_to = Column(String, nullable=True)


class Staff(Base):
    __tablename__ = "staff"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    department = Column(String, nullable=False)
    status = Column(Enum(StaffStatus), nullable=False, default=StaffStatus.OFF_DUTY)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    shift_start = Column(DateTime, nullable=True)
    shift_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Professional details
    license_number = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    specializations = Column(Text, nullable=True)  # JSON string
    hourly_rate = Column(Float, nullable=True)


class Supply(Base):
    __tablename__ = "supplies"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    minimum_threshold = Column(Integer, nullable=False, default=10)
    maximum_capacity = Column(Integer, nullable=False, default=100)
    unit_cost = Column(Float, nullable=False, default=0.0)
    supplier = Column(String, nullable=True)
    location = Column(String, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    status = Column(Enum(SupplyStatus), nullable=False, default=SupplyStatus.IN_STOCK)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    batch_number = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    storage_requirements = Column(String, nullable=True)


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supply_id = Column(String, ForeignKey("supplies.id"), nullable=False)
    transaction_type = Column(String, nullable=False)  # "stock_in", "stock_out", "adjustment"
    quantity = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    performed_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    supply = relationship("Supply", backref="transactions")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=False)
    maintenance_type = Column(String, nullable=False)  # "preventive", "corrective", "emergency"
    description = Column(Text, nullable=True)
    performed_by = Column(String, nullable=True)
    cost = Column(Float, nullable=True)
    date_performed = Column(DateTime, default=datetime.utcnow)
    next_due_date = Column(DateTime, nullable=True)
    
    equipment = relationship("Equipment", backref="maintenance_records")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String, nullable=False)  # "bed_shortage", "equipment_maintenance", "supply_low", "staff_shortage"
    severity = Column(String, nullable=False)  # "low", "medium", "high", "critical"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)  # Reference to bed, equipment, staff, or supply ID
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
