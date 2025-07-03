"""
Database CRUD operations for the Hospital Operations & Logistics Platform.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException

from .models import (
    Bed, Equipment, Staff, Supply, InventoryTransaction, 
    MaintenanceRecord, Alert, BedStatus, EquipmentStatus, 
    StaffStatus, SupplyStatus
)
from ..models.bed_models import BedCreate, BedUpdate
from ..models.equipment_models import EquipmentCreate, EquipmentUpdate
from ..models.staff_models import StaffCreate, StaffUpdate
from ..models.supply_models import SupplyCreate, SupplyUpdate

logger = logging.getLogger(__name__)


class CRUDBase:
    """Base CRUD operations."""
    
    def __init__(self, model):
        self.model = model
    
    def get(self, db: Session, id: str):
        """Get a single item by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ):
        """Get multiple items with pagination and filters."""
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in):
        """Create a new item."""
        try:
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict()
            else:
                obj_data = obj_in
            
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {e}")
            raise HTTPException(status_code=400, detail="Item already exists or constraint violation")
    
    def update(self, db: Session, *, db_obj, obj_in):
        """Update an existing item."""
        try:
            if hasattr(obj_in, 'dict'):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error during update: {e}")
            raise HTTPException(status_code=400, detail="Update constraint violation")
    
    def delete(self, db: Session, *, id: str):
        """Delete an item by ID."""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return obj
        return None


class CRUDBed(CRUDBase):
    """CRUD operations for beds."""
    
    def __init__(self):
        super().__init__(Bed)
    
    def get_available_beds(self, db: Session, department: Optional[str] = None):
        """Get all available beds, optionally filtered by department."""
        query = db.query(Bed).filter(Bed.status == BedStatus.AVAILABLE)
        if department:
            query = query.filter(Bed.department == department)
        return query.all()
    
    def get_beds_by_department(self, db: Session, department: str):
        """Get all beds in a specific department."""
        return db.query(Bed).filter(Bed.department == department).all()
    
    def assign_bed(self, db: Session, bed_id: str, patient_id: str):
        """Assign a bed to a patient."""
        bed = self.get(db, bed_id)
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")
        
        if bed.status != BedStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Bed is not available")
        
        bed.status = BedStatus.OCCUPIED
        bed.patient_id = patient_id
        bed.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(bed)
        return bed
    
    def release_bed(self, db: Session, bed_id: str):
        """Release a bed (make it available)."""
        bed = self.get(db, bed_id)
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")
        
        bed.status = BedStatus.AVAILABLE
        bed.patient_id = None
        bed.last_cleaned = datetime.utcnow()
        bed.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(bed)
        return bed
    
    def get_occupancy_rate(self, db: Session, department: Optional[str] = None):
        """Calculate bed occupancy rate."""
        query = db.query(Bed)
        if department:
            query = query.filter(Bed.department == department)
        
        total_beds = query.count()
        occupied_beds = query.filter(Bed.status == BedStatus.OCCUPIED).count()
        
        return {
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "occupancy_rate": (occupied_beds / total_beds * 100) if total_beds > 0 else 0
        }


class CRUDEquipment(CRUDBase):
    """CRUD operations for equipment."""
    
    def __init__(self):
        super().__init__(Equipment)
    
    def get_available_equipment(self, db: Session, equipment_type: Optional[str] = None, department: Optional[str] = None):
        """Get available equipment, optionally filtered by type and department."""
        query = db.query(Equipment).filter(Equipment.status == EquipmentStatus.AVAILABLE)
        
        if equipment_type:
            query = query.filter(Equipment.equipment_type == equipment_type)
        if department:
            query = query.filter(Equipment.department == department)
        
        return query.all()
    
    def assign_equipment(self, db: Session, equipment_id: str, assigned_to: str):
        """Assign equipment to a staff member or department."""
        equipment = self.get(db, equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        if equipment.status != EquipmentStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Equipment is not available")
        
        equipment.status = EquipmentStatus.IN_USE
        equipment.assigned_to = assigned_to
        equipment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(equipment)
        return equipment
    
    def release_equipment(self, db: Session, equipment_id: str):
        """Release equipment (make it available)."""
        equipment = self.get(db, equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        equipment.status = EquipmentStatus.AVAILABLE
        equipment.assigned_to = None
        equipment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(equipment)
        return equipment
    
    def schedule_maintenance(self, db: Session, equipment_id: str, maintenance_date: datetime):
        """Schedule maintenance for equipment."""
        equipment = self.get(db, equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        equipment.next_maintenance = maintenance_date
        if equipment.status == EquipmentStatus.AVAILABLE:
            equipment.status = EquipmentStatus.MAINTENANCE
        equipment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(equipment)
        return equipment
    
    def get_maintenance_due(self, db: Session, days_ahead: int = 7):
        """Get equipment that has maintenance due within specified days."""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        return db.query(Equipment).filter(
            and_(
                Equipment.next_maintenance <= cutoff_date,
                Equipment.next_maintenance >= datetime.utcnow()
            )
        ).all()


class CRUDStaff(CRUDBase):
    """CRUD operations for staff."""
    
    def __init__(self):
        super().__init__(Staff)
    
    def get_available_staff(self, db: Session, role: Optional[str] = None, department: Optional[str] = None):
        """Get available staff, optionally filtered by role and department."""
        query = db.query(Staff).filter(Staff.status == StaffStatus.AVAILABLE)
        
        if role:
            query = query.filter(Staff.role == role)
        if department:
            query = query.filter(Staff.department == department)
        
        return query.all()
    
    def get_on_duty_staff(self, db: Session, department: Optional[str] = None):
        """Get staff currently on duty."""
        query = db.query(Staff).filter(Staff.status == StaffStatus.ON_DUTY)
        
        if department:
            query = query.filter(Staff.department == department)
        
        return query.all()
    
    def assign_shift(self, db: Session, staff_id: str, shift_start: datetime, shift_end: datetime):
        """Assign a shift to a staff member."""
        staff = self.get(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        staff.shift_start = shift_start
        staff.shift_end = shift_end
        staff.status = StaffStatus.ON_DUTY
        staff.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(staff)
        return staff
    
    def end_shift(self, db: Session, staff_id: str):
        """End a staff member's shift."""
        staff = self.get(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        staff.status = StaffStatus.OFF_DUTY
        staff.shift_start = None
        staff.shift_end = None
        staff.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(staff)
        return staff
    
    def get_department_coverage(self, db: Session, department: str):
        """Get staffing coverage for a department."""
        total_staff = db.query(Staff).filter(Staff.department == department).count()
        on_duty_staff = db.query(Staff).filter(
            and_(
                Staff.department == department,
                Staff.status == StaffStatus.ON_DUTY
            )
        ).count()
        
        return {
            "department": department,
            "total_staff": total_staff,
            "on_duty_staff": on_duty_staff,
            "coverage_rate": (on_duty_staff / total_staff * 100) if total_staff > 0 else 0
        }


class CRUDSupply(CRUDBase):
    """CRUD operations for supplies."""
    
    def __init__(self):
        super().__init__(Supply)
    
    def get_low_stock_supplies(self, db: Session):
        """Get supplies that are low in stock."""
        return db.query(Supply).filter(
            Supply.current_stock <= Supply.minimum_threshold
        ).all()
    
    def get_expired_supplies(self, db: Session):
        """Get supplies that have expired."""
        return db.query(Supply).filter(
            and_(
                Supply.expiry_date <= datetime.utcnow(),
                Supply.expiry_date.isnot(None)
            )
        ).all()
    
    def get_expiring_soon(self, db: Session, days_ahead: int = 30):
        """Get supplies expiring within specified days."""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        return db.query(Supply).filter(
            and_(
                Supply.expiry_date <= cutoff_date,
                Supply.expiry_date > datetime.utcnow()
            )
        ).all()
    
    def update_stock(self, db: Session, supply_id: str, quantity_change: int, reason: str, performed_by: str):
        """Update supply stock and create transaction record."""
        supply = self.get(db, supply_id)
        if not supply:
            raise HTTPException(status_code=404, detail="Supply not found")
        
        # Create transaction record
        transaction = InventoryTransaction(
            supply_id=supply_id,
            transaction_type="stock_in" if quantity_change > 0 else "stock_out",
            quantity=abs(quantity_change),
            reason=reason,
            performed_by=performed_by
        )
        
        # Update stock
        supply.current_stock += quantity_change
        
        # Update status based on stock level
        if supply.current_stock <= 0:
            supply.status = SupplyStatus.OUT_OF_STOCK
        elif supply.current_stock <= supply.minimum_threshold:
            supply.status = SupplyStatus.LOW_STOCK
        else:
            supply.status = SupplyStatus.IN_STOCK
        
        # Check for expiry
        if supply.expiry_date and supply.expiry_date <= datetime.utcnow():
            supply.status = SupplyStatus.EXPIRED
        
        supply.updated_at = datetime.utcnow()
        
        db.add(transaction)
        db.commit()
        db.refresh(supply)
        
        return supply
    
    def get_stock_by_category(self, db: Session, category: str):
        """Get all supplies in a specific category."""
        return db.query(Supply).filter(Supply.category == category).all()


class CRUDAlert(CRUDBase):
    """CRUD operations for alerts."""
    
    def __init__(self):
        super().__init__(Alert)
    
    def get_active_alerts(self, db: Session, severity: Optional[str] = None):
        """Get all active (unresolved) alerts."""
        query = db.query(Alert).filter(Alert.is_resolved == False)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        return query.order_by(desc(Alert.created_at)).all()
    
    def resolve_alert(self, db: Session, alert_id: int, resolved_by: str):
        """Resolve an alert."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        db.commit()
        db.refresh(alert)
        return alert
    
    def create_alert(self, db: Session, alert_type: str, severity: str, title: str, 
                    description: str = None, department: str = None, entity_id: str = None):
        """Create a new alert."""
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            department=department,
            entity_id=entity_id
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert


# Initialize CRUD instances
bed_crud = CRUDBed()
equipment_crud = CRUDEquipment()
staff_crud = CRUDStaff()
supply_crud = CRUDSupply()
alert_crud = CRUDAlert()
