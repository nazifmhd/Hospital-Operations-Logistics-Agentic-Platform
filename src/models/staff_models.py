"""
Staff data models for Hospital Operations Platform
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class StaffStatusEnum(str, Enum):
    """Staff status enumeration matching database"""
    AVAILABLE = "available"
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    ON_BREAK = "on_break"


class StaffRole(str, Enum):
    """Staff role enumeration"""
    NURSE = "nurse"
    DOCTOR = "doctor"
    SPECIALIST = "specialist"
    TECHNICIAN = "technician"
    THERAPIST = "therapist"
    ADMINISTRATOR = "administrator"
    SUPPORT = "support"


class SkillLevel(str, Enum):
    """Staff skill level enumeration"""
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


class ShiftType(str, Enum):
    """Shift type enumeration"""
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"
    TWELVE_HOUR = "twelve_hour"


class AssignmentStatus(str, Enum):
    """Assignment status enumeration"""
    ASSIGNED = "assigned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Staff(BaseModel):
    """Staff member data model"""
    staff_id: str = Field(..., description="Unique staff identifier")
    employee_id: str = Field(..., description="Employee ID")
    name: str = Field(..., description="Staff member name")
    
    # Role and qualifications
    role: StaffRole
    department: str = Field(..., description="Primary department")
    skills: List[str] = Field(default_factory=list, description="List of skills/certifications")
    skill_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)
    specializations: List[str] = Field(default_factory=list)
    
    # Scheduling preferences
    shift_preference: ShiftType = Field(default=ShiftType.DAY)
    max_hours_per_week: int = Field(default=40, gt=0, le=80)
    preferred_units: List[str] = Field(default_factory=list)
    
    # Current status
    is_available: bool = Field(default=True)
    current_location: Optional[str] = None
    current_assignment: Optional[str] = Field(None, description="Current assignment ID")
    
    # Workload tracking
    current_hours_this_week: int = Field(default=0, ge=0)
    current_patient_load: int = Field(default=0, ge=0)
    overtime_hours: float = Field(default=0.0, ge=0.0)
    
    # Certifications and compliance
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    certification_expiry: Optional[datetime] = None
    compliance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Contact and emergency
    contact_info: Optional[Dict[str, str]] = Field(default_factory=dict)
    emergency_contact: Optional[Dict[str, str]] = Field(default_factory=dict)
    
    # Administrative
    hire_date: Optional[datetime] = None
    last_performance_review: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StaffAssignment(BaseModel):
    """Staff assignment data model"""
    assignment_id: str = Field(..., description="Unique assignment ID")
    staff_id: str = Field(..., description="Staff member ID")
    
    # Assignment details
    department: str = Field(..., description="Assignment department")
    unit: Optional[str] = None
    shift_type: ShiftType
    
    # Timing
    start_time: datetime
    end_time: datetime
    duration_hours: float = Field(..., gt=0)
    
    # Workload
    patient_load: int = Field(default=0, ge=0)
    required_skills: List[str] = Field(default_factory=list)
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Priority and status
    priority_level: int = Field(default=1, ge=1, le=5)
    status: AssignmentStatus = Field(default=AssignmentStatus.ASSIGNED)
    
    # Context
    supervisor: Optional[str] = Field(None, description="Supervising staff ID")
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkloadMetrics(BaseModel):
    """Staff workload metrics model"""
    staff_id: str = Field(..., description="Staff member ID")
    
    # Workload indicators
    current_patient_load: int = Field(default=0, ge=0)
    max_patient_capacity: int = Field(..., gt=0)
    utilization_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Time tracking
    hours_worked_today: float = Field(default=0.0, ge=0.0)
    hours_worked_this_week: float = Field(default=0.0, ge=0.0)
    overtime_hours: float = Field(default=0.0, ge=0.0)
    
    # Performance indicators
    efficiency_score: float = Field(default=0.8, ge=0.0, le=1.0)
    stress_level: float = Field(default=0.3, ge=0.0, le=1.0)
    fatigue_level: float = Field(default=0.2, ge=0.0, le=1.0)
    
    # Quality metrics
    patient_satisfaction_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    incident_count: int = Field(default=0, ge=0)
    compliance_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class StaffRequest(BaseModel):
    """Staff allocation request model"""
    request_id: str = Field(..., description="Unique request ID")
    
    # Request details
    requesting_department: str = Field(..., description="Department making request")
    requesting_manager: Optional[str] = Field(None, description="Manager making request")
    
    # Requirements
    required_role: StaffRole
    required_skills: List[str] = Field(default_factory=list)
    minimum_skill_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)
    shift_type: ShiftType
    
    # Timing
    needed_by: datetime
    duration_hours: float = Field(..., gt=0)
    flexibility_minutes: int = Field(default=0, ge=0, description="Flexibility in start time")
    
    # Context
    priority: str = Field(default="normal")  # low, normal, high, urgent, critical
    patient_load: int = Field(default=0, ge=0)
    special_requirements: Optional[str] = None
    
    # Response
    assigned_staff: Optional[str] = Field(None, description="Assigned staff member ID")
    status: str = Field(default="pending")  # pending, assigned, fulfilled, cancelled
    response_time: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ShiftSchedule(BaseModel):
    """Shift schedule model"""
    schedule_id: str = Field(..., description="Unique schedule ID")
    staff_id: str = Field(..., description="Staff member ID")
    
    # Schedule details
    date: datetime
    shift_type: ShiftType
    start_time: datetime
    end_time: datetime
    duration_hours: float = Field(..., gt=0)
    
    # Assignment details
    department: str
    unit: Optional[str] = None
    role_assignment: Optional[str] = None
    
    # Status
    is_confirmed: bool = Field(default=False)
    is_completed: bool = Field(default=False)
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    
    # Context
    notes: Optional[str] = None
    created_by: Optional[str] = Field(None, description="Schedule creator ID")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StaffPerformance(BaseModel):
    """Staff performance tracking model"""
    performance_id: str = Field(..., description="Unique performance record ID")
    staff_id: str = Field(..., description="Staff member ID")
    
    # Performance period
    period_start: datetime
    period_end: datetime
    
    # Metrics
    patient_satisfaction_avg: Optional[float] = Field(None, ge=0.0, le=5.0)
    efficiency_score: float = Field(default=0.8, ge=0.0, le=1.0)
    attendance_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    punctuality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Quality indicators
    incident_count: int = Field(default=0, ge=0)
    compliment_count: int = Field(default=0, ge=0)
    training_hours: float = Field(default=0.0, ge=0.0)
    
    # Goals and development
    goals_met: int = Field(default=0, ge=0)
    total_goals: int = Field(default=0, ge=0)
    development_activities: List[str] = Field(default_factory=list)
    
    # Overall rating
    overall_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    reviewer_id: Optional[str] = Field(None, description="Performance reviewer ID")
    review_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Create and Update models for CRUD operations

class StaffCreate(BaseModel):
    """Model for creating a new staff member"""
    id: str
    name: str
    role: str
    department: str
    status: StaffStatusEnum = StaffStatusEnum.OFF_DUTY
    email: Optional[str] = None
    phone: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    specializations: Optional[str] = None
    hourly_rate: Optional[float] = None


class StaffUpdate(BaseModel):
    """Model for updating an existing staff member"""
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    status: Optional[StaffStatusEnum] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    specializations: Optional[str] = None
    hourly_rate: Optional[float] = None


class StaffResponse(BaseModel):
    """Response model for staff data that matches the database structure"""
    id: str
    name: str
    role: str
    department: str
    status: StaffStatusEnum
    email: Optional[str] = None
    phone: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    specializations: Optional[str] = None
    hourly_rate: Optional[float] = None
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with SQLAlchemy


# Response models for API
class StaffStatusResponse(BaseModel):
    """Staff status summary response"""
    total_staff: int
    available_staff: int
    active_assignments: int
    average_workload: float
    staff_by_department: Dict[str, int]
    workload_alerts: int


class StaffListResponse(BaseModel):
    """Staff list response"""
    staff: List[Staff]
    total_count: int
    page: int = 1
    page_size: int = 50


class StaffAllocationResponse(BaseModel):
    """Staff allocation response"""
    success: bool
    assignment: Optional[StaffAssignment] = None
    alternatives: Optional[List[Staff]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    message: Optional[str] = None


class WorkloadResponse(BaseModel):
    """Workload analysis response"""
    staff_id: str
    metrics: WorkloadMetrics
    recommendations: List[str] = Field(default_factory=list)
    alert_level: str = Field(default="normal")  # normal, warning, critical
