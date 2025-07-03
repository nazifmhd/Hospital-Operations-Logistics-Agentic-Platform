"""
Staff Allocation Agent for Hospital Operations Platform
Manages staff scheduling, workload optimization, and skill-based assignments
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from src.core.base_agent import BaseAgent, AgentMessage, AgentEvent


class ShiftType(str, Enum):
    """Staff shift types"""
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"
    TWELVE_HOUR = "twelve_hour"


class StaffRole(str, Enum):
    """Staff roles and specializations"""
    NURSE = "nurse"
    DOCTOR = "doctor"
    SPECIALIST = "specialist"
    TECHNICIAN = "technician"
    THERAPIST = "therapist"
    ADMINISTRATOR = "administrator"
    SUPPORT = "support"


class SkillLevel(str, Enum):
    """Staff skill levels"""
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


@dataclass
class StaffMember:
    """Staff member data model"""
    id: str
    name: str
    role: StaffRole
    skills: List[str]
    skill_level: SkillLevel
    department: str
    shift_preference: ShiftType
    max_hours_per_week: int
    current_hours_this_week: int
    certification_expiry: Optional[datetime]
    is_available: bool
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StaffAssignment:
    """Staff assignment data model"""
    id: str
    staff_id: str
    department: str
    shift_type: ShiftType
    start_time: datetime
    end_time: datetime
    patient_load: int
    required_skills: List[str]
    priority_level: int
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkloadMetrics:
    """Workload calculation metrics"""
    staff_id: str
    current_patient_load: int
    skill_utilization: float
    overtime_hours: float
    stress_level: float
    efficiency_score: float


class StaffAllocationAgent(BaseAgent):
    """Agent responsible for optimizing staff allocation and scheduling"""
    
    def __init__(self, agent_id: str = "staff_allocation_agent"):
        super().__init__(agent_id)
        self.staff_members: Dict[str, StaffMember] = {}
        self.assignments: Dict[str, StaffAssignment] = {}
        self.workload_metrics: Dict[str, WorkloadMetrics] = {}
        
        # Algorithm parameters
        self.max_patient_ratio = {
            StaffRole.NURSE: 8,
            StaffRole.DOCTOR: 15,
            StaffRole.SPECIALIST: 12,
            StaffRole.TECHNICIAN: 20,
            StaffRole.THERAPIST: 6
        }
        
        # Initialize with mock data
        asyncio.create_task(self._initialize_mock_data())
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for staff allocation"""
        try:
            if message.message_type == "staff_request":
                return await self._handle_staff_request(message)
            elif message.message_type == "workload_update":
                return await self._handle_workload_update(message)
            elif message.message_type == "schedule_optimization":
                return await self._handle_schedule_optimization(message)
            elif message.message_type == "emergency_staffing":
                return await self._handle_emergency_staffing(message)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing message {message.id}: {e}")
            return AgentMessage(
                id=f"error_{datetime.utcnow().isoformat()}",
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="error",
                content={"error": str(e), "original_message_id": message.id}
            )
    
    async def _handle_staff_request(self, message: AgentMessage) -> AgentMessage:
        """Handle requests for staff allocation"""
        content = message.content
        department = content.get("department")
        required_skills = content.get("required_skills", [])
        shift_type = content.get("shift_type", ShiftType.DAY)
        priority = content.get("priority", 1)
        
        # Find best matching staff
        available_staff = await self._find_available_staff(
            department=department,
            required_skills=required_skills,
            shift_type=shift_type
        )
        
        # Optimize assignment
        optimal_assignment = await self._optimize_staff_assignment(
            available_staff, content
        )
        
        return AgentMessage(
            id=f"staff_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="staff_assignment",
            content={
                "assignment": optimal_assignment,
                "confidence": 0.9,
                "alternatives": available_staff[:3]
            }
        )
    
    async def _handle_workload_update(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle workload updates and rebalancing"""
        content = message.content
        staff_id = content.get("staff_id")
        new_patient_load = content.get("patient_load", 0)
        
        if staff_id in self.workload_metrics:
            # Update workload metrics
            self.workload_metrics[staff_id].current_patient_load = new_patient_load
            await self._calculate_workload_metrics(staff_id)
            
            # Check if rebalancing is needed
            if await self._needs_rebalancing(staff_id):
                return await self._suggest_workload_rebalancing(staff_id)
        
        return None
    
    async def _handle_schedule_optimization(self, message: AgentMessage) -> AgentMessage:
        """Handle schedule optimization requests"""
        content = message.content
        timeframe = content.get("timeframe", "week")
        department = content.get("department")
        
        optimized_schedule = await self._optimize_schedule(timeframe, department)
        
        return AgentMessage(
            id=f"schedule_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="schedule_optimization",
            content={
                "schedule": optimized_schedule,
                "efficiency_improvement": 0.15,
                "cost_savings": 5000
            }
        )
    
    async def _handle_emergency_staffing(self, message: AgentMessage) -> AgentMessage:
        """Handle emergency staffing requests"""
        content = message.content
        emergency_type = content.get("emergency_type")
        location = content.get("location")
        urgency = content.get("urgency", "high")
        
        emergency_staff = await self._allocate_emergency_staff(
            emergency_type, location, urgency
        )
        
        return AgentMessage(
            id=f"emergency_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="emergency_staffing",
            content={
                "allocated_staff": emergency_staff,
                "response_time": "5 minutes",
                "backup_options": []
            }
        )
    
    async def _find_available_staff(
        self, 
        department: str, 
        required_skills: List[str], 
        shift_type: ShiftType
    ) -> List[StaffMember]:
        """Find available staff matching criteria"""
        available_staff = []
        
        for staff in self.staff_members.values():
            if (staff.is_available and 
                staff.department == department and
                staff.shift_preference == shift_type and
                all(skill in staff.skills for skill in required_skills)):
                available_staff.append(staff)
        
        # Sort by skill level and availability
        available_staff.sort(
            key=lambda s: (s.skill_level.value, -s.current_hours_this_week)
        )
        
        return available_staff
    
    async def _optimize_staff_assignment(
        self, 
        available_staff: List[StaffMember], 
        requirements: Dict[str, Any]
    ) -> Optional[StaffAssignment]:
        """Optimize staff assignment based on multiple criteria"""
        if not available_staff:
            return None
        
        # Simple optimization: select best qualified with lowest workload
        best_staff = available_staff[0]
        
        assignment = StaffAssignment(
            id=f"assignment_{datetime.utcnow().isoformat()}",
            staff_id=best_staff.id,
            department=requirements.get("department"),
            shift_type=requirements.get("shift_type", ShiftType.DAY),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=8),
            patient_load=requirements.get("patient_load", 5),
            required_skills=requirements.get("required_skills", []),
            priority_level=requirements.get("priority", 1),
            status="assigned"
        )
        
        self.assignments[assignment.id] = assignment
        return assignment
    
    async def _calculate_workload_metrics(self, staff_id: str) -> None:
        """Calculate comprehensive workload metrics for staff member"""
        if staff_id not in self.staff_members:
            return
        
        staff = self.staff_members[staff_id]
        max_load = self.max_patient_ratio.get(staff.role, 10)
        
        current_load = sum(
            a.patient_load for a in self.assignments.values() 
            if a.staff_id == staff_id and a.status == "active"
        )
        
        # Calculate metrics
        skill_utilization = min(current_load / max_load, 1.0)
        overtime_hours = max(0, staff.current_hours_this_week - 40)
        stress_level = (skill_utilization * 0.6) + (overtime_hours / 20 * 0.4)
        efficiency_score = 1.0 - (stress_level * 0.3)
        
        self.workload_metrics[staff_id] = WorkloadMetrics(
            staff_id=staff_id,
            current_patient_load=current_load,
            skill_utilization=skill_utilization,
            overtime_hours=overtime_hours,
            stress_level=stress_level,
            efficiency_score=efficiency_score
        )
    
    async def _needs_rebalancing(self, staff_id: str) -> bool:
        """Determine if workload rebalancing is needed"""
        if staff_id not in self.workload_metrics:
            return False
        
        metrics = self.workload_metrics[staff_id]
        return (metrics.stress_level > 0.8 or 
                metrics.skill_utilization > 0.9 or
                metrics.overtime_hours > 10)
    
    async def _suggest_workload_rebalancing(self, staff_id: str) -> AgentMessage:
        """Suggest workload rebalancing strategies"""
        suggestions = [
            "Consider redistributing patients to less loaded staff",
            "Schedule additional break time",
            "Assign support staff for non-critical tasks"
        ]
        
        return AgentMessage(
            id=f"rebalancing_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id="system",
            message_type="workload_alert",
            content={
                "staff_id": staff_id,
                "alert_type": "workload_exceeded",
                "suggestions": suggestions,
                "urgency": "medium"
            }
        )
    
    async def _optimize_schedule(self, timeframe: str, department: str) -> Dict[str, Any]:
        """Optimize staff schedule for given timeframe and department"""
        # Simplified schedule optimization
        schedule = {}
        
        for staff in self.staff_members.values():
            if department and staff.department != department:
                continue
                
            schedule[staff.id] = {
                "shifts": self._generate_optimal_shifts(staff),
                "total_hours": 40,
                "efficiency_score": 0.85
            }
        
        return schedule
    
    def _generate_optimal_shifts(self, staff: StaffMember) -> List[Dict[str, Any]]:
        """Generate optimal shifts for a staff member"""
        shifts = []
        for i in range(5):  # 5 day work week
            shifts.append({
                "date": (datetime.utcnow() + timedelta(days=i)).isoformat(),
                "start_time": "08:00",
                "end_time": "16:00",
                "shift_type": staff.shift_preference.value
            })
        return shifts
    
    async def _allocate_emergency_staff(
        self, 
        emergency_type: str, 
        location: str, 
        urgency: str
    ) -> List[Dict[str, Any]]:
        """Allocate staff for emergency situations"""
        emergency_staff = []
        
        # Find available emergency response staff
        for staff in self.staff_members.values():
            if (staff.is_available and 
                "emergency" in staff.skills and
                staff.location == location):
                emergency_staff.append(staff.to_dict())
                
                if len(emergency_staff) >= 3:  # Allocate 3 for emergency
                    break
        
        return emergency_staff
    
    async def _initialize_mock_data(self) -> None:
        """Initialize with mock staff data"""
        mock_staff = [
            StaffMember(
                id="staff_001",
                name="Sarah Johnson",
                role=StaffRole.NURSE,
                skills=["patient_care", "medication", "emergency"],
                skill_level=SkillLevel.SENIOR,
                department="Emergency",
                shift_preference=ShiftType.DAY,
                max_hours_per_week=40,
                current_hours_this_week=32,
                certification_expiry=datetime.utcnow() + timedelta(days=365),
                is_available=True,
                location="ER"
            ),
            StaffMember(
                id="staff_002",
                name="Dr. Michael Chen",
                role=StaffRole.DOCTOR,
                skills=["surgery", "diagnosis", "emergency"],
                skill_level=SkillLevel.EXPERT,
                department="Surgery",
                shift_preference=ShiftType.DAY,
                max_hours_per_week=50,
                current_hours_this_week=45,
                certification_expiry=datetime.utcnow() + timedelta(days=730),
                is_available=True,
                location="OR"
            ),
            StaffMember(
                id="staff_003",
                name="Emily Rodriguez",
                role=StaffRole.TECHNICIAN,
                skills=["x_ray", "ct_scan", "mri"],
                skill_level=SkillLevel.INTERMEDIATE,
                department="Radiology",
                shift_preference=ShiftType.EVENING,
                max_hours_per_week=40,
                current_hours_this_week=28,
                certification_expiry=datetime.utcnow() + timedelta(days=180),
                is_available=True,
                location="Radiology"
            )
        ]
        
        for staff in mock_staff:
            self.staff_members[staff.id] = staff
            await self._calculate_workload_metrics(staff.id)
        
        self.logger.info(f"Initialized with {len(mock_staff)} staff members")
    
    async def get_staff_status(self) -> Dict[str, Any]:
        """Get comprehensive staff status"""
        return {
            "total_staff": len(self.staff_members),
            "available_staff": len([s for s in self.staff_members.values() if s.is_available]),
            "active_assignments": len([a for a in self.assignments.values() if a.status == "active"]),
            "average_workload": sum(m.skill_utilization for m in self.workload_metrics.values()) / len(self.workload_metrics) if self.workload_metrics else 0,
            "staff_by_department": self._get_staff_by_department(),
            "workload_alerts": len([m for m in self.workload_metrics.values() if m.stress_level > 0.8])
        }
    
    def _get_staff_by_department(self) -> Dict[str, int]:
        """Get staff count by department"""
        departments = {}
        for staff in self.staff_members.values():
            departments[staff.department] = departments.get(staff.department, 0) + 1
        return departments
    
    async def get_staff_members(self) -> List[Dict[str, Any]]:
        """Get all staff members"""
        return [staff.to_dict() for staff in self.staff_members.values()]
    
    async def get_assignments(self) -> List[Dict[str, Any]]:
        """Get all current assignments"""
        return [assignment.to_dict() for assignment in self.assignments.values()]
    
    async def allocate_staff(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate staff based on requirements"""
        message = AgentMessage(
            id=f"allocation_request_{datetime.utcnow().isoformat()}",
            sender_id="api",
            recipient_id=self.agent_id,
            message_type="staff_request",
            content=requirements
        )
        
        response = await self._handle_staff_request(message)
        return response.content if response else {"error": "No suitable staff found"}
