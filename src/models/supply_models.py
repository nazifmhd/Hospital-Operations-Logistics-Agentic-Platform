"""
Supply inventory data models for Hospital Operations Platform
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SupplyStatusEnum(str, Enum):
    """Supply status enumeration matching database"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    EXPIRED = "expired"


class SupplyCategory(str, Enum):
    """Supply category enumeration"""
    MEDICAL_DEVICES = "medical_devices"
    PHARMACEUTICALS = "pharmaceuticals"
    SURGICAL_SUPPLIES = "surgical_supplies"
    PERSONAL_PROTECTIVE = "personal_protective"
    LABORATORY = "laboratory"
    CLEANING = "cleaning"
    OFFICE = "office"
    FOOD_SERVICE = "food_service"


class SupplyStatus(str, Enum):
    """Supply status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ON_ORDER = "on_order"
    EXPIRED = "expired"
    RECALLED = "recalled"
    QUARANTINED = "quarantined"


class UrgencyLevel(str, Enum):
    """Urgency level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class SupplyItem(BaseModel):
    """Supply item data model"""
    item_id: str = Field(..., description="Unique supply item identifier")
    name: str = Field(..., description="Supply item name")
    description: Optional[str] = None
    category: SupplyCategory
    
    # Classification
    sku: Optional[str] = Field(None, description="Stock Keeping Unit")
    manufacturer: Optional[str] = None
    brand: Optional[str] = None
    model_number: Optional[str] = None
    
    # Stock information
    current_stock: int = Field(default=0, ge=0)
    min_threshold: int = Field(..., gt=0, description="Minimum stock threshold")
    max_capacity: int = Field(..., gt=0, description="Maximum stock capacity")
    reorder_point: int = Field(..., gt=0, description="Automatic reorder point")
    reorder_quantity: int = Field(..., gt=0, description="Standard reorder quantity")
    
    # Pricing
    unit_cost: float = Field(..., gt=0, description="Cost per unit")
    last_purchase_price: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="USD")
    
    # Location and storage
    primary_location: str = Field(..., description="Primary storage location")
    secondary_locations: List[str] = Field(default_factory=list)
    storage_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Expiry and batch tracking
    has_expiry: bool = Field(default=False)
    expiry_date: Optional[datetime] = None
    lot_number: Optional[str] = None
    batch_number: Optional[str] = None
    
    # Usage tracking
    usage_rate_per_day: float = Field(default=0.0, ge=0.0)
    last_used: Optional[datetime] = None
    total_consumed: int = Field(default=0, ge=0)
    
    # Supply chain
    supplier_id: str = Field(..., description="Primary supplier ID")
    alternative_suppliers: List[str] = Field(default_factory=list)
    lead_time_days: int = Field(default=7, gt=0)
    
    # Status and compliance
    status: SupplyStatus = Field(default=SupplyStatus.IN_STOCK)
    is_critical: bool = Field(default=False, description="Critical supply item")
    requires_prescription: bool = Field(default=False)
    controlled_substance: bool = Field(default=False)
    
    # Tracking
    last_restocked: Optional[datetime] = None
    last_audit: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def days_until_empty(self) -> float:
        """Calculate days until stock runs out"""
        if self.usage_rate_per_day <= 0:
            return float('inf')
        return self.current_stock / self.usage_rate_per_day

    @property
    def stock_percentage(self) -> float:
        """Calculate current stock as percentage of max capacity"""
        return (self.current_stock / self.max_capacity) * 100 if self.max_capacity > 0 else 0


class Supplier(BaseModel):
    """Supplier data model"""
    supplier_id: str = Field(..., description="Unique supplier identifier")
    name: str = Field(..., description="Supplier name")
    contact_person: Optional[str] = None
    
    # Contact information
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[Dict[str, str]] = Field(default_factory=dict)
    
    # Business details
    tax_id: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    quality_rating: float = Field(default=3.0, ge=0.0, le=5.0)
    
    # Performance metrics
    on_time_delivery_rate: float = Field(default=0.95, ge=0.0, le=1.0)
    order_accuracy_rate: float = Field(default=0.98, ge=0.0, le=1.0)
    average_lead_time_days: int = Field(default=7, gt=0)
    
    # Status
    is_active: bool = Field(default=True)
    is_preferred: bool = Field(default=False)
    payment_terms: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProcurementOrder(BaseModel):
    """Procurement order data model"""
    order_id: str = Field(..., description="Unique order identifier")
    supplier_id: str = Field(..., description="Supplier ID")
    
    # Order details
    order_number: Optional[str] = None
    items: List[Dict[str, Any]] = Field(..., description="List of items with quantities and prices")
    
    # Financial
    subtotal: float = Field(..., ge=0)
    tax_amount: float = Field(default=0.0, ge=0.0)
    shipping_cost: float = Field(default=0.0, ge=0.0)
    total_cost: float = Field(..., ge=0)
    
    # Timing
    order_date: datetime = Field(default_factory=datetime.utcnow)
    requested_delivery_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    
    # Priority and urgency
    urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM)
    priority_notes: Optional[str] = None
    
    # Status tracking
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    approval_status: str = Field(default="pending")  # pending, approved, rejected
    approved_by: Optional[str] = Field(None, description="Approver staff ID")
    approval_date: Optional[datetime] = None
    
    # Delivery tracking
    tracking_number: Optional[str] = None
    shipping_method: Optional[str] = None
    delivery_address: Optional[Dict[str, str]] = Field(default_factory=dict)
    
    # Notes and documentation
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    order_reason: Optional[str] = None
    
    # Administrative
    created_by: str = Field(..., description="Staff ID who created the order")
    department: str = Field(..., description="Ordering department")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryTransaction(BaseModel):
    """Inventory transaction record model"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    item_id: str = Field(..., description="Supply item ID")
    
    # Transaction details
    transaction_type: str = Field(..., description="Type: receipt, consumption, adjustment, transfer")
    quantity: int = Field(..., description="Quantity change (positive for addition, negative for consumption)")
    unit_cost: Optional[float] = Field(None, gt=0)
    
    # Context
    location: str = Field(..., description="Location where transaction occurred")
    department: Optional[str] = None
    staff_id: Optional[str] = Field(None, description="Staff member involved")
    patient_id: Optional[str] = Field(None, description="Patient if applicable")
    
    # Source/destination
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    reference_order_id: Optional[str] = Field(None, description="Related order if applicable")
    
    # Tracking
    lot_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    
    # Administrative
    reason: Optional[str] = None
    notes: Optional[str] = None
    authorized_by: Optional[str] = Field(None, description="Authorization staff ID")
    
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryAlert(BaseModel):
    """Inventory alert model"""
    alert_id: str = Field(..., description="Unique alert identifier")
    item_id: str = Field(..., description="Supply item ID")
    
    # Alert details
    alert_type: str = Field(..., description="Type: low_stock, expiring, expired, recalled")
    severity: UrgencyLevel
    message: str = Field(..., description="Alert message")
    
    # Context
    current_stock: Optional[int] = Field(None, ge=0)
    threshold_value: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    
    # Status
    is_resolved: bool = Field(default=False)
    resolved_by: Optional[str] = Field(None, description="Staff ID who resolved")
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    # Escalation
    escalated: bool = Field(default=False)
    escalated_to: Optional[str] = Field(None, description="Escalated to staff ID")
    escalation_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UsagePattern(BaseModel):
    """Supply usage pattern analysis model"""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    item_id: str = Field(..., description="Supply item ID")
    
    # Pattern analysis
    department: str = Field(..., description="Department using the supply")
    average_daily_usage: float = Field(default=0.0, ge=0.0)
    peak_usage_periods: List[str] = Field(default_factory=list)
    seasonal_factors: Dict[str, float] = Field(default_factory=dict)
    
    # Trends
    trend_direction: str = Field(default="stable")  # increasing, decreasing, stable
    trend_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    volatility_score: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Predictions
    predicted_usage_next_week: float = Field(default=0.0, ge=0.0)
    predicted_usage_next_month: float = Field(default=0.0, ge=0.0)
    
    # Analysis period
    analysis_start_date: datetime
    analysis_end_date: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# Create and Update models for CRUD operations

class SupplyCreate(BaseModel):
    """Model for creating a new supply item"""
    id: str
    name: str
    category: str
    current_stock: int = 0
    minimum_threshold: int
    maximum_capacity: int
    unit_cost: float
    supplier: Optional[str] = None
    location: str
    expiry_date: Optional[datetime] = None
    status: SupplyStatusEnum = SupplyStatusEnum.IN_STOCK
    batch_number: Optional[str] = None
    manufacturer: Optional[str] = None
    storage_requirements: Optional[str] = None


class SupplyUpdate(BaseModel):
    """Model for updating an existing supply item"""
    name: Optional[str] = None
    category: Optional[str] = None
    current_stock: Optional[int] = None
    minimum_threshold: Optional[int] = None
    maximum_capacity: Optional[int] = None
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None
    location: Optional[str] = None
    expiry_date: Optional[datetime] = None
    status: Optional[SupplyStatusEnum] = None
    batch_number: Optional[str] = None
    manufacturer: Optional[str] = None
    storage_requirements: Optional[str] = None


class SupplyResponse(BaseModel):
    """Response model for supply data that matches the database structure"""
    id: str
    name: str
    category: str
    current_stock: int
    minimum_threshold: int
    maximum_capacity: int
    unit_cost: float
    supplier: Optional[str] = None
    location: str
    expiry_date: Optional[datetime] = None
    status: SupplyStatusEnum
    created_at: datetime
    updated_at: datetime
    batch_number: Optional[str] = None
    manufacturer: Optional[str] = None
    storage_requirements: Optional[str] = None
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with SQLAlchemy


# Response models for API
class InventoryStatusResponse(BaseModel):
    """Inventory status summary response"""
    total_items: int
    low_stock_items: int
    out_of_stock_items: int
    expired_items: int
    total_inventory_value: float
    active_orders: int
    alerts_count: int
    categories: Dict[str, int]


class SupplyListResponse(BaseModel):
    """Supply list response"""
    supplies: List[SupplyItem]
    total_count: int
    page: int = 1
    page_size: int = 50


class LowStockResponse(BaseModel):
    """Low stock items response"""
    low_stock_items: List[SupplyItem]
    critical_items: List[SupplyItem]
    recommended_orders: List[Dict[str, Any]]
    total_estimated_cost: float


class ProcurementResponse(BaseModel):
    """Procurement order response"""
    success: bool
    order: Optional[ProcurementOrder] = None
    estimated_delivery: Optional[datetime] = None
    total_cost: float = 0.0
    message: Optional[str] = None


class ConsumptionResponse(BaseModel):
    """Supply consumption response"""
    success: bool
    remaining_stock: int = 0
    needs_reorder: bool = False
    days_until_empty: float = 0.0
    message: Optional[str] = None
