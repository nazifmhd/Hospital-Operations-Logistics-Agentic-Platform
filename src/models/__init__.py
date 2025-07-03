"""
Data models for Hospital Operations Platform
"""

from .bed_models import *
from .equipment_models import *
from .staff_models import *
from .supply_models import *

__all__ = [
    # Bed models
    "BedResponse", "BedCreate", "BedUpdate", "PatientAdmission", "BedAssignment", "DischargeEvent",
    "BedUtilizationMetrics", "BedCapacityForecast",
    
    # Equipment models
    "Equipment", "EquipmentStatus", "EquipmentType", "EquipmentLocation",
    "MaintenanceRecord", "EquipmentRequest", "EquipmentUsage",
    "EquipmentStatusResponse", "EquipmentListResponse", "EquipmentTrackingResponse",
    "EquipmentAllocationResponse",
    
    # Staff models
    "Staff", "StaffRole", "SkillLevel", "ShiftType", "StaffAssignment",
    "WorkloadMetrics", "StaffRequest", "ShiftSchedule", "StaffPerformance",
    "StaffStatusResponse", "StaffListResponse", "StaffAllocationResponse",
    "WorkloadResponse",
    
    # Supply models
    "SupplyItem", "SupplyCategory", "SupplyStatus", "UrgencyLevel",
    "Supplier", "ProcurementOrder", "InventoryTransaction", "InventoryAlert",
    "UsagePattern", "InventoryStatusResponse", "SupplyListResponse",
    "LowStockResponse", "ProcurementResponse", "ConsumptionResponse"
]
