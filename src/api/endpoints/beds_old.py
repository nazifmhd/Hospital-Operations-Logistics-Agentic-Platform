"""
Bed management endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class AdmissionRequest(BaseModel):
    patient_id: str
    acuity_score: float
    isolation_requirements: List[str] = []
    equipment_needs: List[str] = []
    care_level: str = "standard"
    preferred_unit: Optional[str] = None


class DischargeRequest(BaseModel):
    patient_id: str
    bed_id: str
    discharge_disposition: str
    cleaning_required: bool = True


@router.get("/status")
async def get_bed_status(
    unit_id: Optional[str] = Query(None, description="Filter by unit ID"),
    status: Optional[str] = Query(None, description="Filter by bed status")
) -> Dict[str, Any]:
    """Get current bed status"""
    # This would typically query the database
    # For now, return mock data
    
    mock_beds = [
        {
            "bed_id": "BED_001",
            "unit_id": "ICU_01",
            "room_number": "101",
            "status": "occupied",
            "patient_id": "PAT_12345",
            "bed_type": "icu"
        },
        {
            "bed_id": "BED_002", 
            "unit_id": "ICU_01",
            "room_number": "102",
            "status": "available",
            "patient_id": None,
            "bed_type": "icu"
        },
        {
            "bed_id": "BED_003",
            "unit_id": "MED_01", 
            "room_number": "201",
            "status": "dirty",
            "patient_id": None,
            "bed_type": "standard"
        }
    ]
    
    # Apply filters
    filtered_beds = mock_beds
    if unit_id:
        filtered_beds = [b for b in filtered_beds if b["unit_id"] == unit_id]
    if status:
        filtered_beds = [b for b in filtered_beds if b["status"] == status]
    
    # Calculate summary statistics
    total_beds = len(filtered_beds)
    occupied_beds = len([b for b in filtered_beds if b["status"] == "occupied"])
    available_beds = len([b for b in filtered_beds if b["status"] == "available"])
    
    return {
        "beds": filtered_beds,
        "summary": {
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "occupancy_rate": occupied_beds / total_beds if total_beds > 0 else 0
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/admission")
async def request_admission(admission: AdmissionRequest, request: Request) -> Dict[str, Any]:
    """Request bed assignment for patient admission"""
    try:
        from core.base_agent import AgentEvent
        
        # Create admission event
        event = AgentEvent(
            agent_id="api",
            event_type="patient_admission_request",
            data=admission.dict()
        )
        
        # Process through orchestrator
        orchestrator = request.app.state.orchestrator
        result = await orchestrator.process_external_event(event)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process admission: {str(e)}")


@router.post("/discharge")
async def process_discharge(discharge: DischargeRequest, request: Request) -> Dict[str, Any]:
    """Process patient discharge"""
    try:
        from core.base_agent import AgentEvent
        
        # Create discharge event
        event = AgentEvent(
            agent_id="api",
            event_type="patient_discharge",
            data=discharge.dict()
        )
        
        # Process through orchestrator
        orchestrator = request.app.state.orchestrator
        result = await orchestrator.process_external_event(event)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process discharge: {str(e)}")


@router.get("/utilization")
async def get_bed_utilization(
    unit_id: Optional[str] = Query(None),
    days: int = Query(7, description="Number of days to include")
) -> Dict[str, Any]:
    """Get bed utilization metrics"""
    # Mock utilization data
    return {
        "unit_id": unit_id or "all",
        "period_days": days,
        "metrics": {
            "average_occupancy_rate": 0.82,
            "peak_occupancy_rate": 0.95,
            "average_length_of_stay": 4.2,
            "bed_turnover_rate": 1.8,
            "total_admissions": 156,
            "total_discharges": 148
        },
        "daily_trends": [
            {"date": "2025-07-01", "occupancy_rate": 0.85},
            {"date": "2025-07-02", "occupancy_rate": 0.78}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/forecast")
async def get_bed_demand_forecast(
    hours: int = Query(24, description="Forecast horizon in hours"),
    unit_id: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Get bed demand forecast"""
    # Mock forecast data
    return {
        "unit_id": unit_id or "all",
        "forecast_horizon_hours": hours,
        "predicted_demand": [75, 78, 82, 85, 88, 90],  # Hourly predictions
        "confidence_intervals": {
            "lower": [70, 73, 77, 80, 83, 85],
            "upper": [80, 83, 87, 90, 93, 95]
        },
        "peak_periods": [
            {"start_hour": 8, "end_hour": 12, "predicted_demand": 92},
            {"start_hour": 18, "end_hour": 22, "predicted_demand": 88}
        ],
        "alerts": [
            {
                "type": "capacity_shortage",
                "hour": 10,
                "message": "Predicted capacity shortage at 10:00 AM"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{bed_id}")
async def get_bed_details(bed_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific bed"""
    # Mock bed details
    return {
        "bed_id": bed_id,
        "unit_id": "ICU_01",
        "room_number": "101",
        "bed_number": "A",
        "status": "occupied",
        "bed_type": "icu",
        "patient_id": "PAT_12345",
        "capabilities": {
            "has_telemetry": True,
            "has_oxygen": True,
            "has_isolation": False,
            "is_icu_capable": True
        },
        "location": {
            "floor": "1",
            "wing": "North",
            "distance_to_nurses_station": 15
        },
        "maintenance": {
            "last_cleaned": "2025-07-02T06:00:00Z",
            "next_maintenance": "2025-07-15T00:00:00Z",
            "maintenance_status": "up_to_date"
        },
        "current_assignment": {
            "patient_id": "PAT_12345",
            "admission_date": "2025-07-01T14:30:00Z",
            "estimated_discharge": "2025-07-05T10:00:00Z",
            "acuity_score": 3.5
        },
        "timestamp": datetime.utcnow().isoformat()
    }
