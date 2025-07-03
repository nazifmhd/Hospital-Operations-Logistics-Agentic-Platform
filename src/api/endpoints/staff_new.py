"""
Staff management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.crud import staff_crud
from ...models.staff_models import Staff, StaffCreate, StaffUpdate
from ...agents.staff_allocation_agent import StaffAllocationAgent

router = APIRouter()

# Initialize the staff allocation agent
staff_agent = StaffAllocationAgent()


@router.get("/", response_model=List[Staff])
async def get_staff(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get all staff with optional filtering."""
    filters = {}
    if department:
        filters["department"] = department
    if role:
        filters["role"] = role
    if status:
        filters["status"] = status
    
    staff = staff_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    return staff


@router.get("/{staff_id}", response_model=Staff)
async def get_staff_member(staff_id: str, db: Session = Depends(get_db)):
    """Get a specific staff member by ID."""
    staff = staff_crud.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff


@router.post("/", response_model=Staff)
async def create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    """Create a new staff member."""
    return staff_crud.create(db, obj_in=staff)


@router.put("/{staff_id}", response_model=Staff)
async def update_staff(
    staff_id: str, 
    staff_update: StaffUpdate, 
    db: Session = Depends(get_db)
):
    """Update a staff member."""
    staff = staff_crud.get(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return staff_crud.update(db, db_obj=staff, obj_in=staff_update)


@router.delete("/{staff_id}")
async def delete_staff(staff_id: str, db: Session = Depends(get_db)):
    """Delete a staff member."""
    staff = staff_crud.delete(db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return {"message": "Staff member deleted successfully"}


@router.get("/available/", response_model=List[Staff])
async def get_available_staff(
    role: Optional[str] = Query(None, description="Filter by role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Get all available staff."""
    return staff_crud.get_available_staff(db, role=role, department=department)


@router.get("/on-duty/", response_model=List[Staff])
async def get_on_duty_staff(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Get all staff currently on duty."""
    return staff_crud.get_on_duty_staff(db, department=department)


@router.post("/{staff_id}/assign-shift")
async def assign_shift(
    staff_id: str,
    shift_start: str,  # ISO format datetime string
    shift_end: str,    # ISO format datetime string
    db: Session = Depends(get_db)
):
    """Assign a shift to a staff member."""
    from datetime import datetime
    
    try:
        start_dt = datetime.fromisoformat(shift_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(shift_end.replace('Z', '+00:00'))
        
        staff = staff_crud.assign_shift(
            db, 
            staff_id=staff_id, 
            shift_start=start_dt, 
            shift_end=end_dt
        )
        return {
            "message": f"Shift assigned to staff member {staff_id}",
            "staff": staff
        }
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )


@router.post("/{staff_id}/end-shift")
async def end_shift(staff_id: str, db: Session = Depends(get_db)):
    """End a staff member's shift."""
    staff = staff_crud.end_shift(db, staff_id=staff_id)
    return {
        "message": f"Shift ended for staff member {staff_id}",
        "staff": staff
    }


@router.get("/department/{department}/coverage")
async def get_department_coverage(department: str, db: Session = Depends(get_db)):
    """Get staffing coverage for a department."""
    return staff_crud.get_department_coverage(db, department=department)


@router.get("/analytics/workload")
async def get_workload_analytics(
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)
):
    """Get staff workload analytics."""
    try:
        # Get workload analytics from agent
        analytics = await staff_agent.get_workload_analytics(
            department=department,
            role=role
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/predictions/demand")
async def predict_staffing_demand(
    department: Optional[str] = Query(None, description="Department to predict for"),
    hours_ahead: int = Query(24, description="Hours to predict ahead"),
    db: Session = Depends(get_db)
):
    """Predict staffing demand."""
    try:
        # Get current staff data
        staff = staff_crud.get_multi(db)
        
        # Use agent for predictions
        predictions = await staff_agent.predict_staffing_demand([
            {
                "id": s.id,
                "name": s.name,
                "role": s.role,
                "department": s.department,
                "status": s.status.value,
                "shift_start": s.shift_start.isoformat() if s.shift_start else None,
                "shift_end": s.shift_end.isoformat() if s.shift_end else None
            }
            for s in staff
        ], hours_ahead=hours_ahead, department=department)
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/optimization/scheduling")
async def optimize_staff_scheduling(
    department: Optional[str] = Query(None, description="Department to optimize for"),
    db: Session = Depends(get_db)
):
    """Get optimized staff scheduling recommendations."""
    try:
        # Get current staff data
        staff = staff_crud.get_multi(db)
        
        # Use agent for optimization
        optimization = await staff_agent.optimize_staff_allocation([
            {
                "id": s.id,
                "name": s.name,
                "role": s.role,
                "department": s.department,
                "status": s.status.value,
                "experience_years": s.experience_years or 0,
                "hourly_rate": s.hourly_rate or 0
            }
            for s in staff
        ])
        
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
