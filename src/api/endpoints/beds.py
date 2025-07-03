"""
Bed management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.crud import bed_crud
from ...models.bed_models import BedCreate, BedUpdate, BedResponse
from ...agents.bed_management_agent import BedManagementAgent

router = APIRouter()

# Initialize the bed management agent lazily
bed_agent = None


def get_bed_agent():
    """Get or create the bed management agent instance."""
    global bed_agent
    if bed_agent is None:
        try:
            bed_agent = BedManagementAgent()
        except Exception as e:
            # Log the error but don't fail the API
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize bed management agent: {e}")
            bed_agent = None
    return bed_agent


@router.get("/", response_model=List[BedResponse])
async def get_beds(
    skip: int = Query(0, ge=0, description="Number of beds to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of beds to return"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get all beds with optional filtering."""
    filters = {}
    if department:
        filters["department"] = department
    if status:
        filters["status"] = status
    
    beds = bed_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    return beds


@router.get("/{bed_id}", response_model=BedResponse)
async def get_bed(bed_id: str, db: Session = Depends(get_db)):
    """Get a specific bed by ID."""
    bed = bed_crud.get(db, id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed


@router.post("/", response_model=BedResponse)
async def create_bed(bed: BedCreate, db: Session = Depends(get_db)):
    """Create a new bed."""
    return bed_crud.create(db, obj_in=bed)


@router.put("/{bed_id}", response_model=BedResponse)
async def update_bed(bed_id: str, bed_update: BedUpdate, db: Session = Depends(get_db)):
    """Update a bed."""
    bed = bed_crud.get(db, id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    
    return bed_crud.update(db, db_obj=bed, obj_in=bed_update)


@router.delete("/{bed_id}")
async def delete_bed(bed_id: str, db: Session = Depends(get_db)):
    """Delete a bed."""
    bed = bed_crud.delete(db, id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return {"message": "Bed deleted successfully"}


@router.get("/available/", response_model=List[BedResponse])
async def get_available_beds(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Get all available beds."""
    return bed_crud.get_available_beds(db, department=department)


@router.post("/{bed_id}/assign")
async def assign_bed(
    bed_id: str,
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Assign a bed to a patient."""
    bed = bed_crud.assign_bed(db, bed_id=bed_id, patient_id=patient_id)
    return {"message": f"Bed {bed_id} assigned to patient {patient_id}", "bed": bed}


@router.post("/{bed_id}/release")
async def release_bed(bed_id: str, db: Session = Depends(get_db)):
    """Release a bed (make it available)."""
    bed = bed_crud.release_bed(db, bed_id=bed_id)
    return {"message": f"Bed {bed_id} released and available", "bed": bed}


@router.get("/department/{department}/", response_model=List[BedResponse])
async def get_beds_by_department(department: str, db: Session = Depends(get_db)):
    """Get all beds in a specific department."""
    return bed_crud.get_beds_by_department(db, department=department)


@router.get("/analytics/occupancy")
async def get_bed_occupancy(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Get bed occupancy analytics."""
    return bed_crud.get_occupancy_rate(db, department=department)


@router.get("/predictions/demand")
async def predict_bed_demand(
    department: Optional[str] = Query(None, description="Department to predict for"),
    hours_ahead: int = Query(24, description="Hours to predict ahead")
):
    """Predict bed demand using ML models."""
    try:
        # Use the bed management agent for predictions
        agent = get_bed_agent()
        if agent is None:
            raise HTTPException(status_code=503, detail="Bed management agent not available")
        
        demand_prediction = await agent.predict_bed_demand(
            department=department,
            hours_ahead=hours_ahead
        )
        return demand_prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/optimization/allocation")
async def optimize_bed_allocation(
    db: Session = Depends(get_db)
):
    """Get optimized bed allocation recommendations."""
    try:
        # Get current bed data
        beds = bed_crud.get_multi(db)
        
        # Use agent for optimization
        agent = get_bed_agent()
        if agent is None:
            raise HTTPException(status_code=503, detail="Bed management agent not available")
        
        optimization = await agent.optimize_bed_allocation([
            {
                "id": bed.id,
                "department": bed.department,
                "status": bed.status.value,
                "bed_type": bed.bed_type,
                "room_number": bed.room_number
            }
            for bed in beds
        ])
        
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
