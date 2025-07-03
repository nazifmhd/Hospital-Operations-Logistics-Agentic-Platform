"""
Equipment data models for Hospital Operations Platform
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class EquipmentStatus(str, Enum):
    """Equipment status enumeration"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"


# Base Equipment model for responses
class EquipmentBase(BaseModel):
    """Base equipment model"""
    name: str = Field(..., description="Equipment name")
    equipment_type: str = Field(..., description="Type of equipment")
    department: str = Field(..., description="Department")
    location: str = Field(..., description="Current location")
    manufacturer: Optional[str] = Field(None, description="Manufacturer")
    model: Optional[str] = Field(None, description="Equipment model")
    serial_number: Optional[str] = Field(None, description="Serial number")
    purchase_date: Optional[datetime] = Field(None, description="Purchase date")
    usage_hours: Optional[float] = Field(None, description="Total usage hours")
    maintenance_cost: Optional[float] = Field(None, description="Maintenance cost")
    assigned_to: Optional[str] = Field(None, description="Currently assigned to")


# Equipment creation model
class EquipmentCreate(EquipmentBase):
    """Equipment creation model"""
    id: str = Field(..., description="Unique equipment identifier")


# Equipment update model
class EquipmentUpdate(BaseModel):
    """Equipment update model"""
    name: Optional[str] = None
    equipment_type: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    usage_hours: Optional[float] = None
    maintenance_cost: Optional[float] = None
    assigned_to: Optional[str] = None


# Equipment response model
class Equipment(EquipmentBase):
    """Equipment response model"""
    id: str = Field(..., description="Unique equipment identifier")
    status: EquipmentStatus = Field(..., description="Equipment status")
    last_maintenance: Optional[datetime] = Field(None, description="Last maintenance date")
    next_maintenance: Optional[datetime] = Field(None, description="Next maintenance due")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
