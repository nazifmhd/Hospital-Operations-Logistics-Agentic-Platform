"""
Supply management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.crud import supply_crud
from ...models.supply_models import SupplyItem, SupplyCreate, SupplyUpdate, SupplyResponse
from ...agents.supply_inventory_agent import SupplyInventoryAgent

router = APIRouter()

# Agent instance will be created on demand
_supply_agent = None

def get_supply_agent():
    """Get or create supply inventory agent instance"""
    global _supply_agent
    if _supply_agent is None:
        _supply_agent = SupplyInventoryAgent()
    return _supply_agent


@router.get("/", response_model=List[SupplyResponse])
async def get_supplies(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: Session = Depends(get_db)
):
    """Get all supplies with optional filtering."""
    filters = {}
    if category:
        filters["category"] = category
    if status:
        filters["status"] = status
    if location:
        filters["location"] = location
    
    supplies = supply_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    return supplies


@router.get("/{supply_id}", response_model=SupplyResponse)
async def get_supply(supply_id: str, db: Session = Depends(get_db)):
    """Get a specific supply by ID."""
    supply = supply_crud.get(db, id=supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Supply not found")
    return supply


@router.post("/", response_model=SupplyResponse)
async def create_supply(supply: SupplyCreate, db: Session = Depends(get_db)):
    """Create a new supply."""
    return supply_crud.create(db, obj_in=supply)


@router.put("/{supply_id}", response_model=SupplyResponse)
async def update_supply(
    supply_id: str, 
    supply_update: SupplyUpdate, 
    db: Session = Depends(get_db)
):
    """Update a supply."""
    supply = supply_crud.get(db, id=supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Supply not found")
    
    return supply_crud.update(db, db_obj=supply, obj_in=supply_update)


@router.delete("/{supply_id}")
async def delete_supply(supply_id: str, db: Session = Depends(get_db)):
    """Delete a supply."""
    supply = supply_crud.delete(db, id=supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Supply not found")
    return {"message": "Supply deleted successfully"}


@router.get("/low-stock/", response_model=List[SupplyResponse])
async def get_low_stock_supplies(db: Session = Depends(get_db)):
    """Get all supplies that are low in stock."""
    return supply_crud.get_low_stock_supplies(db)


@router.get("/expired/", response_model=List[SupplyResponse])
async def get_expired_supplies(db: Session = Depends(get_db)):
    """Get all expired supplies."""
    return supply_crud.get_expired_supplies(db)


@router.get("/expiring-soon/", response_model=List[SupplyResponse])
async def get_expiring_soon(
    days_ahead: int = Query(30, description="Days ahead to check for expiry"),
    db: Session = Depends(get_db)
):
    """Get supplies expiring within specified days."""
    return supply_crud.get_expiring_soon(db, days_ahead=days_ahead)


@router.get("/category/{category}/", response_model=List[SupplyResponse])
async def get_supplies_by_category(category: str, db: Session = Depends(get_db)):
    """Get all supplies in a specific category."""
    return supply_crud.get_stock_by_category(db, category=category)


@router.post("/{supply_id}/update-stock")
async def update_stock(
    supply_id: str,
    quantity_change: int,
    reason: str,
    performed_by: str,
    db: Session = Depends(get_db)
):
    """Update supply stock and create transaction record."""
    supply = supply_crud.update_stock(
        db,
        supply_id=supply_id,
        quantity_change=quantity_change,
        reason=reason,
        performed_by=performed_by
    )
    return {
        "message": f"Stock updated for supply {supply_id}",
        "supply": supply,
        "change": quantity_change,
        "new_stock": supply.current_stock
    }


@router.get("/analytics/inventory")
async def get_inventory_analytics(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get inventory analytics."""
    try:
        # Get inventory analytics from agent
        analytics = await get_supply_agent().get_inventory_analytics(category=category)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/predictions/demand")
async def predict_supply_demand(
    category: Optional[str] = Query(None, description="Category to predict for"),
    days_ahead: int = Query(30, description="Days to predict ahead"),
    db: Session = Depends(get_db)
):
    """Predict supply demand."""
    try:
        # Get current supply data
        supplies = supply_crud.get_multi(db)
        
        # Use agent for predictions
        predictions = await get_supply_agent().predict_supply_demand([
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "current_stock": s.current_stock,
                "minimum_threshold": s.minimum_threshold,
                "maximum_capacity": s.maximum_capacity,
                "unit_cost": s.unit_cost,
                "location": s.location
            }
            for s in supplies
        ], days_ahead=days_ahead, category=category)
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/optimization/procurement")
async def optimize_procurement(
    category: Optional[str] = Query(None, description="Category to optimize for"),
    db: Session = Depends(get_db)
):
    """Get optimized procurement recommendations."""
    try:
        # Get current supply data
        supplies = supply_crud.get_multi(db)
        
        # Use agent for optimization
        optimization = await get_supply_agent().optimize_supply_procurement([
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "current_stock": s.current_stock,
                "minimum_threshold": s.minimum_threshold,
                "maximum_capacity": s.maximum_capacity,
                "unit_cost": s.unit_cost,
                "supplier": s.supplier,
                "location": s.location
            }
            for s in supplies
        ])
        
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/alerts/")
async def get_supply_alerts(db: Session = Depends(get_db)):
    """Get supply-related alerts (low stock, expired, etc.)."""
    try:
        low_stock = supply_crud.get_low_stock_supplies(db)
        expired = supply_crud.get_expired_supplies(db)
        expiring_soon = supply_crud.get_expiring_soon(db, days_ahead=7)
        
        alerts = []
        
        for supply in low_stock:
            alerts.append({
                "type": "low_stock",
                "severity": "high" if supply.current_stock == 0 else "medium",
                "supply_id": supply.id,
                "supply_name": supply.name,
                "current_stock": supply.current_stock,
                "minimum_threshold": supply.minimum_threshold,
                "message": f"{supply.name} is {'out of stock' if supply.current_stock == 0 else 'low in stock'}"
            })
        
        for supply in expired:
            alerts.append({
                "type": "expired",
                "severity": "high",
                "supply_id": supply.id,
                "supply_name": supply.name,
                "expiry_date": supply.expiry_date.isoformat() if supply.expiry_date else None,
                "message": f"{supply.name} has expired"
            })
        
        for supply in expiring_soon:
            alerts.append({
                "type": "expiring_soon",
                "severity": "medium",
                "supply_id": supply.id,
                "supply_name": supply.name,
                "expiry_date": supply.expiry_date.isoformat() if supply.expiry_date else None,
                "message": f"{supply.name} expires soon"
            })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "low_stock_count": len(low_stock),
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")
