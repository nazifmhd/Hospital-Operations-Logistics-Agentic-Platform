"""
Supply Inventory Agent for Hospital Operations Platform
Manages medical supplies, equipment inventory, and automated procurement
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from src.core.base_agent import BaseAgent, AgentMessage, AgentEvent


class SupplyCategory(str, Enum):
    """Supply categories"""
    MEDICAL_DEVICES = "medical_devices"
    PHARMACEUTICALS = "pharmaceuticals" 
    SURGICAL_SUPPLIES = "surgical_supplies"
    PERSONAL_PROTECTIVE = "personal_protective"
    LABORATORY = "laboratory"
    CLEANING = "cleaning"
    OFFICE = "office"
    FOOD_SERVICE = "food_service"


class SupplyStatus(str, Enum):
    """Supply status states"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ON_ORDER = "on_order"
    EXPIRED = "expired"
    RECALLED = "recalled"


class UrgencyLevel(str, Enum):
    """Supply urgency levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SupplyItem:
    """Supply item data model"""
    id: str
    name: str
    category: SupplyCategory
    current_stock: int
    min_threshold: int
    max_capacity: int
    unit_cost: float
    supplier_id: str
    location: str
    expiry_date: Optional[datetime]
    lot_number: Optional[str]
    status: SupplyStatus
    last_restocked: datetime
    usage_rate_per_day: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def days_until_empty(self) -> float:
        """Calculate days until stock runs out based on usage rate"""
        if self.usage_rate_per_day <= 0:
            return float('inf')
        return self.current_stock / self.usage_rate_per_day
    
    @property
    def stock_percentage(self) -> float:
        """Calculate current stock as percentage of max capacity"""
        return (self.current_stock / self.max_capacity) * 100 if self.max_capacity > 0 else 0


@dataclass
class ProcurementOrder:
    """Procurement order data model"""
    id: str
    supplier_id: str
    items: List[Dict[str, Any]]  # item_id, quantity, unit_cost
    total_cost: float
    urgency: UrgencyLevel
    order_date: datetime
    expected_delivery: datetime
    status: str
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UsagePattern:
    """Usage pattern tracking"""
    item_id: str
    department: str
    average_daily_usage: float
    peak_usage_periods: List[str]
    seasonal_factors: Dict[str, float]
    trend_direction: str  # increasing, decreasing, stable


@dataclass
class InventoryAlert:
    """Inventory alert data model"""
    id: str
    item_id: str
    alert_type: str
    severity: UrgencyLevel
    message: str
    created_at: datetime
    resolved: bool = False


class SupplyInventoryAgent(BaseAgent):
    """Agent responsible for managing hospital supply inventory and procurement"""
    
    def __init__(self, agent_id: str = "supply_inventory_agent"):
        super().__init__(agent_id)
        self.inventory: Dict[str, SupplyItem] = {}
        self.procurement_orders: Dict[str, ProcurementOrder] = {}
        self.usage_patterns: Dict[str, UsagePattern] = {}
        self.alerts: Dict[str, InventoryAlert] = {}
        
        # Configuration
        self.auto_procurement_enabled = True
        self.lead_time_days = 3
        self.safety_stock_multiplier = 1.5
        
        # Initialize with mock data
        asyncio.create_task(self._initialize_mock_data())
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for supply management"""
        try:
            if message.message_type == "stock_check":
                return await self._handle_stock_check(message)
            elif message.message_type == "usage_update":
                return await self._handle_usage_update(message)
            elif message.message_type == "procurement_request":
                return await self._handle_procurement_request(message)
            elif message.message_type == "delivery_notification":
                return await self._handle_delivery_notification(message)
            elif message.message_type == "expiry_check":
                return await self._handle_expiry_check(message)
            
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
    
    async def _handle_stock_check(self, message: AgentMessage) -> AgentMessage:
        """Handle stock level check requests"""
        content = message.content
        item_id = content.get("item_id")
        
        if item_id:
            item = self.inventory.get(item_id)
            if item:
                stock_info = {
                    "item": item.to_dict(),
                    "days_until_empty": item.days_until_empty,
                    "stock_percentage": item.stock_percentage,
                    "needs_reorder": item.current_stock <= item.min_threshold
                }
            else:
                stock_info = {"error": "Item not found"}
        else:
            # Return overall stock summary
            stock_info = await self._get_stock_summary()
        
        return AgentMessage(
            id=f"stock_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="stock_status",
            content=stock_info
        )
    
    async def _handle_usage_update(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle supply usage updates"""
        content = message.content
        item_id = content.get("item_id")
        quantity_used = content.get("quantity_used", 0)
        department = content.get("department")
        
        if item_id in self.inventory:
            # Update stock levels
            item = self.inventory[item_id]
            item.current_stock = max(0, item.current_stock - quantity_used)
            
            # Update usage patterns
            await self._update_usage_pattern(item_id, quantity_used, department)
            
            # Check if reorder is needed
            if item.current_stock <= item.min_threshold and self.auto_procurement_enabled:
                await self._trigger_automatic_procurement(item_id)
            
            # Generate alerts if necessary
            await self._check_and_generate_alerts(item_id)
        
        return None
    
    async def _handle_procurement_request(self, message: AgentMessage) -> AgentMessage:
        """Handle procurement requests"""
        content = message.content
        items = content.get("items", [])
        urgency = content.get("urgency", UrgencyLevel.MEDIUM)
        
        # Create procurement order
        order = await self._create_procurement_order(items, urgency)
        
        return AgentMessage(
            id=f"procurement_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="procurement_order",
            content={
                "order": order.to_dict() if order else None,
                "estimated_delivery": (datetime.utcnow() + timedelta(days=self.lead_time_days)).isoformat(),
                "total_cost": order.total_cost if order else 0
            }
        )
    
    async def _handle_delivery_notification(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle delivery notifications"""
        content = message.content
        order_id = content.get("order_id")
        delivered_items = content.get("items", [])
        
        if order_id in self.procurement_orders:
            # Update inventory with delivered items
            for item_info in delivered_items:
                item_id = item_info.get("item_id")
                quantity = item_info.get("quantity", 0)
                
                if item_id in self.inventory:
                    self.inventory[item_id].current_stock += quantity
                    self.inventory[item_id].last_restocked = datetime.utcnow()
                    self.inventory[item_id].status = SupplyStatus.IN_STOCK
            
            # Update order status
            self.procurement_orders[order_id].status = "delivered"
            
            self.logger.info(f"Processed delivery for order {order_id}")
        
        return None
    
    async def _handle_expiry_check(self, message: AgentMessage) -> AgentMessage:
        """Handle expiry date checks"""
        expiring_items = []
        expired_items = []
        
        current_time = datetime.utcnow()
        warning_threshold = current_time + timedelta(days=30)
        
        for item in self.inventory.values():
            if item.expiry_date:
                if item.expiry_date <= current_time:
                    expired_items.append(item.to_dict())
                    item.status = SupplyStatus.EXPIRED
                elif item.expiry_date <= warning_threshold:
                    expiring_items.append(item.to_dict())
        
        return AgentMessage(
            id=f"expiry_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="expiry_report",
            content={
                "expiring_items": expiring_items,
                "expired_items": expired_items,
                "total_expiring_value": sum(item["unit_cost"] * item["current_stock"] for item in expiring_items),
                "total_expired_value": sum(item["unit_cost"] * item["current_stock"] for item in expired_items)
            }
        )
    
    async def _get_stock_summary(self) -> Dict[str, Any]:
        """Get comprehensive stock summary"""
        total_items = len(self.inventory)
        low_stock_items = len([item for item in self.inventory.values() if item.current_stock <= item.min_threshold])
        out_of_stock_items = len([item for item in self.inventory.values() if item.current_stock == 0])
        expired_items = len([item for item in self.inventory.values() if item.status == SupplyStatus.EXPIRED])
        
        total_value = sum(item.current_stock * item.unit_cost for item in self.inventory.values())
        
        return {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "expired_items": expired_items,
            "total_inventory_value": total_value,
            "active_orders": len([order for order in self.procurement_orders.values() if order.status == "pending"]),
            "alerts_count": len([alert for alert in self.alerts.values() if not alert.resolved])
        }
    
    async def _update_usage_pattern(self, item_id: str, quantity_used: int, department: str) -> None:
        """Update usage patterns for predictive analytics"""
        if item_id not in self.usage_patterns:
            self.usage_patterns[item_id] = UsagePattern(
                item_id=item_id,
                department=department or "unknown",
                average_daily_usage=quantity_used,
                peak_usage_periods=[],
                seasonal_factors={},
                trend_direction="stable"
            )
        else:
            pattern = self.usage_patterns[item_id]
            # Simple moving average update
            pattern.average_daily_usage = (pattern.average_daily_usage * 0.9) + (quantity_used * 0.1)
            
            # Update item usage rate
            if item_id in self.inventory:
                self.inventory[item_id].usage_rate_per_day = pattern.average_daily_usage
    
    async def _trigger_automatic_procurement(self, item_id: str) -> None:
        """Trigger automatic procurement for low stock items"""
        if item_id not in self.inventory:
            return
        
        item = self.inventory[item_id]
        
        # Calculate reorder quantity
        days_lead_time = self.lead_time_days
        usage_rate = item.usage_rate_per_day
        safety_stock = usage_rate * days_lead_time * self.safety_stock_multiplier
        reorder_quantity = int(item.max_capacity - item.current_stock + safety_stock)
        
        # Create procurement order
        items = [{"item_id": item_id, "quantity": reorder_quantity, "unit_cost": item.unit_cost}]
        order = await self._create_procurement_order(items, UrgencyLevel.HIGH)
        
        if order:
            item.status = SupplyStatus.ON_ORDER
            self.logger.info(f"Auto-triggered procurement for {item.name}, quantity: {reorder_quantity}")
    
    async def _create_procurement_order(self, items: List[Dict[str, Any]], urgency: UrgencyLevel) -> Optional[ProcurementOrder]:
        """Create a new procurement order"""
        if not items:
            return None
        
        total_cost = sum(item.get("quantity", 0) * item.get("unit_cost", 0) for item in items)
        
        order = ProcurementOrder(
            id=f"order_{datetime.utcnow().isoformat()}",
            supplier_id="default_supplier",
            items=items,
            total_cost=total_cost,
            urgency=urgency,
            order_date=datetime.utcnow(),
            expected_delivery=datetime.utcnow() + timedelta(days=self.lead_time_days),
            status="pending"
        )
        
        self.procurement_orders[order.id] = order
        return order
    
    async def _check_and_generate_alerts(self, item_id: str) -> None:
        """Check and generate inventory alerts"""
        if item_id not in self.inventory:
            return
        
        item = self.inventory[item_id]
        alerts_to_create = []
        
        # Low stock alert
        if item.current_stock <= item.min_threshold:
            alerts_to_create.append({
                "alert_type": "low_stock",
                "severity": UrgencyLevel.HIGH if item.current_stock == 0 else UrgencyLevel.MEDIUM,
                "message": f"{item.name} is running low (Current: {item.current_stock}, Min: {item.min_threshold})"
            })
        
        # Expiry alert
        if item.expiry_date and item.expiry_date <= datetime.utcnow() + timedelta(days=7):
            alerts_to_create.append({
                "alert_type": "expiring_soon",
                "severity": UrgencyLevel.HIGH,
                "message": f"{item.name} expires on {item.expiry_date.strftime('%Y-%m-%d')}"
            })
        
        # Create alerts
        for alert_info in alerts_to_create:
            alert = InventoryAlert(
                id=f"alert_{datetime.utcnow().isoformat()}",
                item_id=item_id,
                alert_type=alert_info["alert_type"],
                severity=alert_info["severity"],
                message=alert_info["message"],
                created_at=datetime.utcnow()
            )
            self.alerts[alert.id] = alert
    
    async def _initialize_mock_data(self) -> None:
        """Initialize with mock supply data"""
        mock_supplies = [
            SupplyItem(
                id="supply_001",
                name="Surgical Gloves (Medium)",
                category=SupplyCategory.SURGICAL_SUPPLIES,
                current_stock=250,
                min_threshold=100,
                max_capacity=1000,
                unit_cost=0.15,
                supplier_id="supplier_001",
                location="Supply Room A",
                expiry_date=datetime.utcnow() + timedelta(days=180),
                lot_number="LOT123456",
                status=SupplyStatus.IN_STOCK,
                last_restocked=datetime.utcnow() - timedelta(days=5),
                usage_rate_per_day=12.5
            ),
            SupplyItem(
                id="supply_002",
                name="N95 Masks",
                category=SupplyCategory.PERSONAL_PROTECTIVE,
                current_stock=50,
                min_threshold=200,
                max_capacity=2000,
                unit_cost=2.50,
                supplier_id="supplier_002",
                location="PPE Storage",
                expiry_date=datetime.utcnow() + timedelta(days=365),
                lot_number="LOT789012",
                status=SupplyStatus.LOW_STOCK,
                last_restocked=datetime.utcnow() - timedelta(days=15),
                usage_rate_per_day=45.0
            ),
            SupplyItem(
                id="supply_003",
                name="Saline Solution 500ml",
                category=SupplyCategory.PHARMACEUTICALS,
                current_stock=300,
                min_threshold=150,
                max_capacity=800,
                unit_cost=3.75,
                supplier_id="supplier_003",
                location="Pharmacy",
                expiry_date=datetime.utcnow() + timedelta(days=90),
                lot_number="LOT345678",
                status=SupplyStatus.IN_STOCK,
                last_restocked=datetime.utcnow() - timedelta(days=3),
                usage_rate_per_day=8.2
            ),
            SupplyItem(
                id="supply_004",
                name="Disposable Syringes 10ml",
                category=SupplyCategory.MEDICAL_DEVICES,
                current_stock=0,
                min_threshold=500,
                max_capacity=5000,
                unit_cost=0.45,
                supplier_id="supplier_001",
                location="Supply Room B",
                expiry_date=datetime.utcnow() + timedelta(days=730),
                lot_number="LOT901234",
                status=SupplyStatus.OUT_OF_STOCK,
                last_restocked=datetime.utcnow() - timedelta(days=20),
                usage_rate_per_day=35.0
            )
        ]
        
        for supply in mock_supplies:
            self.inventory[supply.id] = supply
            await self._update_usage_pattern(supply.id, supply.usage_rate_per_day, "general")
            await self._check_and_generate_alerts(supply.id)
        
        self.logger.info(f"Initialized with {len(mock_supplies)} supply items")
    
    async def get_inventory_status(self) -> Dict[str, Any]:
        """Get comprehensive inventory status"""
        return await self._get_stock_summary()
    
    async def get_all_supplies(self) -> List[Dict[str, Any]]:
        """Get all supply items"""
        return [supply.to_dict() for supply in self.inventory.values()]
    
    async def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Get items with low stock"""
        return [
            supply.to_dict() for supply in self.inventory.values() 
            if supply.current_stock <= supply.min_threshold
        ]
    
    async def get_procurement_orders(self) -> List[Dict[str, Any]]:
        """Get all procurement orders"""
        return [order.to_dict() for order in self.procurement_orders.values()]
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active inventory alerts"""
        return [alert.__dict__ for alert in self.alerts.values() if not alert.resolved]
    
    async def consume_supply(self, item_id: str, quantity: int, department: str = None) -> Dict[str, Any]:
        """Consume supply and update inventory"""
        message = AgentMessage(
            id=f"usage_update_{datetime.utcnow().isoformat()}",
            sender_id="api",
            recipient_id=self.agent_id,
            message_type="usage_update",
            content={
                "item_id": item_id,
                "quantity_used": quantity,
                "department": department
            }
        )
        
        await self._handle_usage_update(message)
        
        if item_id in self.inventory:
            item = self.inventory[item_id]
            return {
                "success": True,
                "remaining_stock": item.current_stock,
                "needs_reorder": item.current_stock <= item.min_threshold,
                "days_until_empty": item.days_until_empty
            }
        else:
            return {"success": False, "error": "Item not found"}
    
    async def create_procurement_order(self, items: List[Dict[str, Any]], urgency: str = "medium") -> Dict[str, Any]:
        """Create a new procurement order"""
        message = AgentMessage(
            id=f"procurement_request_{datetime.utcnow().isoformat()}",
            sender_id="api",
            recipient_id=self.agent_id,
            message_type="procurement_request",
            content={
                "items": items,
                "urgency": urgency
            }
        )
        
        response = await self._handle_procurement_request(message)
        return response.content if response else {"error": "Failed to create order"}
