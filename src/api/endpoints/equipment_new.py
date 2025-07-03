"""
Equipment management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.crud import equipment_crud
from ...models.equipment_models import Equipment, EquipmentCreate, EquipmentUpdate
from ...agents.equipment_tracker_agent import EquipmentTrackerAgent

router = APIRouter()

# Initialize the equipment tracker agent
equipment_agent = EquipmentTrackerAgent()


@router.get("/", response_model=List[Equipment])
async def get_equipment(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    department: Optional[str] = Query(None, description="Filter by department"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get all equipment with optional filtering."""
    filters = {}
    if department:
        filters["department"] = department
    if equipment_type:
        filters["equipment_type"] = equipment_type
    if status:
        filters["status"] = status
    
    equipment = equipment_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    return equipment


@router.get("/{equipment_id}", response_model=Equipment)
async def get_equipment_item(equipment_id: str, db: Session = Depends(get_db)):
    """Get a specific equipment item by ID."""
    equipment = equipment_crud.get(db, id=equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.post("/", response_model=Equipment)
async def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """Create a new equipment item."""
    return equipment_crud.create(db, obj_in=equipment)


@router.put("/{equipment_id}", response_model=Equipment)
async def update_equipment(
    equipment_id: str, 
    equipment_update: EquipmentUpdate, 
    db: Session = Depends(get_db)
):
    """Update an equipment item."""
    equipment = equipment_crud.get(db, id=equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    return equipment_crud.update(db, db_obj=equipment, obj_in=equipment_update)


@router.delete("/{equipment_id}")
async def delete_equipment(equipment_id: str, db: Session = Depends(get_db)):
    """Delete an equipment item."""
    equipment = equipment_crud.delete(db, id=equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment deleted successfully"}


@router.get("/available/", response_model=List[Equipment])
async def get_available_equipment(
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Get all available equipment."""
    return equipment_crud.get_available_equipment(
        db, 
        equipment_type=equipment_type, 
        department=department
    )


@router.post("/{equipment_id}/assign")
async def assign_equipment(
    equipment_id: str,
    assigned_to: str,
    db: Session = Depends(get_db)
):
    """Assign equipment to a staff member or department."""
    equipment = equipment_crud.assign_equipment(
        db, 
        equipment_id=equipment_id, 
        assigned_to=assigned_to
    )
    return {
        "message": f"Equipment {equipment_id} assigned to {assigned_to}", 
        "equipment": equipment
    }


@router.post("/{equipment_id}/release")
async def release_equipment(equipment_id: str, db: Session = Depends(get_db)):
    """Release equipment (make it available)."""
    equipment = equipment_crud.release_equipment(db, equipment_id=equipment_id)
    return {
        "message": f"Equipment {equipment_id} released and available", 
        "equipment": equipment
    }


@router.get("/maintenance/due")
async def get_maintenance_due(
    days_ahead: int = Query(7, description="Days ahead to check for maintenance"),
    db: Session = Depends(get_db)
):
    """Get equipment that has maintenance due."""
    equipment = equipment_crud.get_maintenance_due(db, days_ahead=days_ahead)
    return {
        "equipment": equipment,
        "count": len(equipment),
        "days_ahead": days_ahead
    }


@router.post("/{equipment_id}/maintenance/schedule")
async def schedule_maintenance(
    equipment_id: str,
    maintenance_date: str,  # ISO format datetime string
    db: Session = Depends(get_db)
):
    """Schedule maintenance for equipment."""
    from datetime import datetime
    
    try:
        maintenance_dt = datetime.fromisoformat(maintenance_date.replace('Z', '+00:00'))
        equipment = equipment_crud.schedule_maintenance(
            db, 
            equipment_id=equipment_id, 
            maintenance_date=maintenance_dt
        )
        return {
            "message": f"Maintenance scheduled for equipment {equipment_id}",
            "equipment": equipment
        }
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )


@router.get("/analytics/utilization")
async def get_equipment_utilization(
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Get equipment utilization analytics."""
    try:
        # Get equipment utilization from agent
        utilization = await equipment_agent.get_utilization_analytics(
            equipment_type=equipment_type,
            department=department
        )
        return utilization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/predictions/maintenance")
async def predict_maintenance_needs(
    days_ahead: int = Query(30, description="Days to predict ahead"),
    db: Session = Depends(get_db)
):
    """Predict equipment maintenance needs."""
    try:
        # Get current equipment data
        equipment = equipment_crud.get_multi(db)
        
        # Use agent for predictions
        predictions = await equipment_agent.predict_maintenance_needs([
            {
                "id": eq.id,
                "name": eq.name,
                "equipment_type": eq.equipment_type,
                "usage_hours": eq.usage_hours or 0,
                "last_maintenance": eq.last_maintenance.isoformat() if eq.last_maintenance else None,
                "next_maintenance": eq.next_maintenance.isoformat() if eq.next_maintenance else None
            }
            for eq in equipment
        ])
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/optimization/allocation")
async def optimize_equipment_allocation(
    db: Session = Depends(get_db)
):
    """Get optimized equipment allocation recommendations."""
    try:
        # Get current equipment data
        equipment = equipment_crud.get_multi(db)
        
        # Use agent for optimization
        optimization = await equipment_agent.optimize_equipment_allocation([
            {
                "id": eq.id,
                "name": eq.name,
                "equipment_type": eq.equipment_type,
                "department": eq.department,
                "location": eq.location,
                "status": eq.status.value,
                "assigned_to": eq.assigned_to
            }
            for eq in equipment
        ])
        
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
