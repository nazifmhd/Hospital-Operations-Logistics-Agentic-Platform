"""
Data models for bed management operations
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class BedStatusEnum(str, Enum):
    """Bed status enumeration"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"



class PatientAdmission(BaseModel):
    """Patient admission request model"""
    patient_id: str
    admission_timestamp: datetime = Field(default_factory=datetime.utcnow)
    estimated_length_of_stay: Optional[int] = None  # days
    acuity_score: float = Field(ge=1.0, le=5.0)  # 1-5 scale
    
    # Requirements
    isolation_requirements: List[str] = Field(default_factory=list)
    equipment_needs: List[str] = Field(default_factory=list)
    care_level: str = "standard"  # standard, icu, step_down, etc.
    
    # Preferences
    preferred_unit: Optional[str] = None
    preferred_room_type: Optional[str] = None
    
    # Clinical information
    diagnosis_codes: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    mobility_requirements: Optional[str] = None
    
    # Administrative
    insurance_type: Optional[str] = None
    admission_source: str = "ED"  # ED, Transfer, Direct
    admission_type: str = "inpatient"  # inpatient, observation, outpatient


class BedAssignment(BaseModel):
    """Bed assignment model"""
    assignment_id: str = Field(default_factory=lambda: f"BA_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    patient_id: str
    bed_id: str
    unit_id: str
    
    assignment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    estimated_wait_time: int = 0  # minutes
    assignment_score: float = Field(ge=0.0, le=1.0)  # optimization score
    
    # Assignment details
    assignment_reason: str = "optimal_match"
    assigned_by: str = "bed_management_agent"
    priority_level: int = Field(ge=1, le=5)  # 1=highest, 5=lowest
    
    # Requirements met
    isolation_met: bool = True
    equipment_met: bool = True
    care_level_met: bool = True
    
    # Predicted outcomes
    predicted_satisfaction: Optional[float] = None
    predicted_los: Optional[int] = None  # days


class DischargeEvent(BaseModel):
    """Patient discharge event model"""
    patient_id: str
    bed_id: str
    unit_id: str
    discharge_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Discharge details
    discharge_disposition: str  # home, transfer, skilled_nursing, etc.
    discharge_reason: str
    actual_los: int  # actual length of stay in days
    
    # Bed preparation needed
    cleaning_required: bool = True
    maintenance_required: bool = False
    deep_clean_required: bool = False
    
    # Quality metrics
    patient_satisfaction: Optional[float] = None
    readmission_risk: Optional[float] = None


class BedUtilizationMetrics(BaseModel):
    """Bed utilization metrics model"""
    unit_id: str
    date: datetime
    
    # Utilization metrics
    total_beds: int
    occupied_beds: int
    available_beds: int
    out_of_order_beds: int
    
    # Calculated metrics
    occupancy_rate: float = Field(ge=0.0, le=1.0)
    turnover_rate: float
    average_los: float
    
    # Flow metrics
    admissions_count: int
    discharges_count: int
    transfers_in: int
    transfers_out: int
    
    # Time metrics
    average_wait_time: float  # minutes
    average_turnaround_time: float  # minutes from discharge to ready


class BedCapacityForecast(BaseModel):
    """Bed capacity forecast model"""
    unit_id: str
    forecast_timestamp: datetime = Field(default_factory=datetime.utcnow)
    forecast_horizon_hours: int
    
    # Forecasted metrics
    predicted_occupancy: List[float]  # hourly predictions
    predicted_admissions: List[int]
    predicted_discharges: List[int]
    
    # Confidence intervals
    occupancy_confidence_lower: List[float]
    occupancy_confidence_upper: List[float]
    
    # Alert thresholds
    capacity_shortage_periods: List[datetime]
    peak_demand_periods: List[datetime]
    
    # Model metadata
    model_accuracy: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# Create and Update models for CRUD operations

class BedCreate(BaseModel):
    """Model for creating a new bed"""
    id: str
    room_number: str
    department: str
    bed_type: str
    status: BedStatusEnum = BedStatusEnum.AVAILABLE
    patient_id: Optional[str] = None
    floor: Optional[int] = None
    wing: Optional[str] = None
    isolation_required: bool = False
    special_equipment: Optional[str] = None


class BedUpdate(BaseModel):
    """Model for updating an existing bed"""
    room_number: Optional[str] = None
    department: Optional[str] = None
    bed_type: Optional[str] = None
    status: Optional[BedStatusEnum] = None
    patient_id: Optional[str] = None
    floor: Optional[int] = None
    wing: Optional[str] = None
    isolation_required: Optional[bool] = None
    special_equipment: Optional[str] = None


class BedResponse(BaseModel):
    """Response model for bed data that matches the database structure"""
    id: str
    room_number: str
    department: str
    bed_type: str
    status: BedStatusEnum
    patient_id: Optional[str] = None
    last_cleaned: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    floor: Optional[int] = None
    wing: Optional[str] = None
    isolation_required: bool = False
    special_equipment: Optional[str] = None
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with SQLAlchemy
