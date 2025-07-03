"""
Equipment Tracker Agent for managing medical equipment
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from src.core.base_agent import BaseAgent, AgentMessage, AgentEvent


class EquipmentStatus(str, Enum):
    """Equipment status enumeration"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"
    RESERVED = "reserved"


class EquipmentType(str, Enum):
    """Equipment type enumeration"""
    IV_PUMP = "iv_pump"
    WHEELCHAIR = "wheelchair"
    VENTILATOR = "ventilator"
    MONITOR = "monitor"
    DEFIBRILLATOR = "defibrillator"


@dataclass
class EquipmentItem:
    """Equipment item data model"""
    asset_id: str
    name: str
    equipment_type: EquipmentType
    status: EquipmentStatus
    location: Dict[str, str]
    condition_score: float
    usage_hours: int
    last_maintenance: Optional[datetime]
    utilization_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EquipmentTrackerAgent(BaseAgent):
    """Agent responsible for equipment tracking and optimization"""
    
    def __init__(self, agent_id: str = "equipment_tracker_agent"):
        super().__init__(agent_id)
        self.equipment_inventory: Dict[str, EquipmentItem] = {}
        self.location_history: Dict[str, List[Dict[str, Any]]] = {}
        self.utilization_metrics: Dict[str, float] = {}
        
        # Performance tracking
        self.tracking_accuracy = 0.95
        self.average_utilization = 0.0
        self.maintenance_compliance = 0.0
        
        # Initialize with mock data
        asyncio.create_task(self._initialize_mock_data())
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process equipment tracking related messages"""
        try:
            if message.message_type == "equipment_location_update":
                return await self._handle_location_update(message.content)
            elif message.message_type == "equipment_maintenance_request":
                return await self._handle_maintenance_request(message.content)
            elif message.message_type == "equipment_usage_update":
                return await self._handle_usage_update(message.content)
            elif message.message_type == "equipment_allocation_request":
                return await self._handle_allocation_request(message.content)
            
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
    
    async def _handle_location_update(self, data: Dict[str, Any]) -> AgentMessage:
        """Handle equipment location updates from RTLS"""
        asset_id = data["asset_id"]
        location = data["location"]
        timestamp = data.get("timestamp", datetime.utcnow())
        
        # Update equipment location
        if asset_id in self.equipment_inventory:
            self.equipment_inventory[asset_id].location = location
            
            # Track location history
            if asset_id not in self.location_history:
                self.location_history[asset_id] = []
            self.location_history[asset_id].append({
                "location": location,
                "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp
            })
            
            # Keep only recent history (last 7 days)
            if isinstance(timestamp, datetime):
                cutoff = timestamp - timedelta(days=7)
                self.location_history[asset_id] = [
                    entry for entry in self.location_history[asset_id]
                    if datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')) > cutoff
                ]
        
        return AgentMessage(
            id=f"location_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id="system",
            message_type="location_update_response",
            content={"success": True, "asset_id": asset_id, "location": location}
        )
    
    async def _handle_allocation_request(self, data: Dict[str, Any]) -> AgentMessage:
        """Handle equipment allocation requests"""
        equipment_type = data.get("equipment_type")
        unit_id = data.get("unit_id")
        priority = data.get("priority", "normal")
        
        # Find available equipment
        available_equipment = await self._find_available_equipment(
            equipment_type, unit_id, priority
        )
        
        if available_equipment:
            # Reserve the equipment
            equipment_id = available_equipment.asset_id
            self.equipment_inventory[equipment_id].status = EquipmentStatus.RESERVED
            
            response_content = {
                "success": True,
                "equipment": available_equipment.to_dict(),
                "estimated_delivery_time": 15  # minutes
            }
        else:
            # No equipment available
            alternatives = await self._suggest_equipment_alternatives(equipment_type, unit_id)
            
            response_content = {
                "success": False,
                "reason": "no_equipment_available",
                "alternatives": [alt.to_dict() for alt in alternatives],
                "estimated_wait_time": await self._estimate_equipment_wait_time(equipment_type)
            }
        
        return AgentMessage(
            id=f"allocation_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=data.get("requester_id", "system"),
            message_type="equipment_allocation_response",
            content=response_content
        )
    
    async def _find_available_equipment(
        self, equipment_type: str, unit_id: str, priority: str
    ) -> Optional[EquipmentItem]:
        """Find available equipment of specified type"""
        available_items = []
        
        for equipment in self.equipment_inventory.values():
            if (equipment.equipment_type.value == equipment_type and 
                equipment.status == EquipmentStatus.AVAILABLE):
                
                # Calculate suitability score
                score = await self._calculate_equipment_suitability(
                    equipment, unit_id, priority
                )
                available_items.append((equipment, score))
        
        if available_items:
            # Return the best match
            best_equipment, _ = max(available_items, key=lambda x: x[1])
            return best_equipment
        
        return None
    
    async def _calculate_equipment_suitability(
        self, equipment: EquipmentItem, unit_id: str, priority: str
    ) -> float:
        """Calculate suitability score for equipment assignment"""
        score = 0.0
        
        # Distance factor (closer is better)
        distance_score = await self._calculate_distance_score(equipment.location, unit_id)
        score += distance_score * 0.4
        
        # Condition factor
        score += equipment.condition_score * 0.3
        
        # Utilization factor (less used is better for maintenance)
        utilization_score = 1.0 - equipment.utilization_rate
        score += utilization_score * 0.2
        
        # Priority factor
        if priority == "urgent":
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    async def _calculate_distance_score(self, location: Dict[str, str], unit_id: str) -> float:
        """Calculate distance score between equipment location and target unit"""
        # Simplified distance calculation
        if location.get("unit") == unit_id:
            return 1.0
        elif location.get("floor") == unit_id[:2]:  # Same floor
            return 0.7
        else:
            return 0.3
    
    async def _suggest_equipment_alternatives(
        self, equipment_type: str, unit_id: str
    ) -> List[EquipmentItem]:
        """Suggest alternative equipment options"""
        alternatives = []
        
        # Find equipment that will be available soon
        for equipment in self.equipment_inventory.values():
            if (equipment.equipment_type.value == equipment_type and 
                equipment.status in [EquipmentStatus.IN_USE, EquipmentStatus.RESERVED]):
                alternatives.append(equipment)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    async def _estimate_equipment_wait_time(self, equipment_type: str) -> int:
        """Estimate wait time for equipment type"""
        # Simplified wait time estimation
        utilization = self.utilization_metrics.get(equipment_type, 0.5)
        if utilization > 0.8:
            return 60  # 1 hour
        elif utilization > 0.6:
            return 30  # 30 minutes
        else:
            return 15  # 15 minutes
    
    async def _handle_maintenance_request(self, data: Dict[str, Any]) -> AgentMessage:
        """Handle equipment maintenance requests"""
        asset_id = data.get("asset_id")
        maintenance_type = data.get("maintenance_type", "routine")
        
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            equipment.status = EquipmentStatus.MAINTENANCE
            equipment.last_maintenance = datetime.utcnow()
            
            response_content = {
                "success": True,
                "asset_id": asset_id,
                "maintenance_scheduled": True,
                "estimated_completion": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            }
        else:
            response_content = {
                "success": False,
                "error": "Equipment not found"
            }
        
        return AgentMessage(
            id=f"maintenance_response_{datetime.utcnow().isoformat()}",
            sender_id=self.agent_id,
            recipient_id=data.get("requester_id", "system"),
            message_type="maintenance_response",
            content=response_content
        )
    
    async def _handle_usage_update(self, data: Dict[str, Any]) -> Optional[AgentMessage]:
        """Handle equipment usage updates"""
        asset_id = data.get("asset_id")
        usage_hours = data.get("usage_hours", 0)
        
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            equipment.usage_hours += usage_hours
            
            # Update utilization metrics
            self.utilization_metrics[asset_id] = min(1.0, equipment.usage_hours / (24 * 30))
            
            # Check if maintenance is needed
            if equipment.usage_hours > 1000 and not equipment.last_maintenance:
                return AgentMessage(
                    id=f"maintenance_alert_{datetime.utcnow().isoformat()}",
                    sender_id=self.agent_id,
                    recipient_id="system",
                    message_type="maintenance_alert",
                    content={
                        "asset_id": asset_id,
                        "alert_type": "maintenance_due",
                        "message": f"Equipment {asset_id} requires maintenance"
                    }
                )
        
        return None
    
    async def _initialize_mock_data(self) -> None:
        """Initialize with mock equipment data"""
        mock_equipment = [
            EquipmentItem(
                asset_id="EQ_001",
                name="IV Pump Alpha",
                equipment_type=EquipmentType.IV_PUMP,
                status=EquipmentStatus.AVAILABLE,
                location={"unit": "ICU_01", "room": "101"},
                condition_score=0.9,
                usage_hours=2500,
                last_maintenance=datetime.utcnow() - timedelta(days=30),
                utilization_rate=0.75
            ),
            EquipmentItem(
                asset_id="EQ_002", 
                name="Wheelchair Standard",
                equipment_type=EquipmentType.WHEELCHAIR,
                status=EquipmentStatus.IN_USE,
                location={"unit": "MED_01", "room": "205"},
                condition_score=0.8,
                usage_hours=1200,
                last_maintenance=datetime.utcnow() - timedelta(days=60),
                utilization_rate=0.60
            ),
            EquipmentItem(
                asset_id="EQ_003",
                name="Ventilator Pro",
                equipment_type=EquipmentType.VENTILATOR,
                status=EquipmentStatus.AVAILABLE,
                location={"unit": "ICU_01", "room": "storage"},
                condition_score=0.95,
                usage_hours=800,
                last_maintenance=datetime.utcnow() - timedelta(days=15),
                utilization_rate=0.85
            )
        ]
        
        for equipment in mock_equipment:
            self.equipment_inventory[equipment.asset_id] = equipment
            self.utilization_metrics[equipment.asset_id] = equipment.utilization_rate
        
        self.logger.info(f"Initialized with {len(mock_equipment)} equipment items")
    
    async def get_equipment_status(self) -> Dict[str, Any]:
        """Get comprehensive equipment status"""
        total_equipment = len(self.equipment_inventory)
        available = len([eq for eq in self.equipment_inventory.values() if eq.status == EquipmentStatus.AVAILABLE])
        in_use = len([eq for eq in self.equipment_inventory.values() if eq.status == EquipmentStatus.IN_USE])
        maintenance = len([eq for eq in self.equipment_inventory.values() if eq.status == EquipmentStatus.MAINTENANCE])
        out_of_order = len([eq for eq in self.equipment_inventory.values() if eq.status == EquipmentStatus.OUT_OF_ORDER])
        
        if self.utilization_metrics:
            avg_utilization = sum(self.utilization_metrics.values()) / len(self.utilization_metrics)
        else:
            avg_utilization = 0.0
        
        return {
            "total_equipment": total_equipment,
            "available": available,
            "in_use": in_use,
            "in_maintenance": maintenance,
            "out_of_order": out_of_order,
            "average_utilization": avg_utilization,
            "tracking_accuracy": self.tracking_accuracy,
            "maintenance_compliance": self.maintenance_compliance
        }
    
    async def get_all_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment items"""
        return [equipment.to_dict() for equipment in self.equipment_inventory.values()]
    
    async def track_equipment(self, asset_id: str) -> Dict[str, Any]:
        """Track specific equipment by asset ID"""
        if asset_id not in self.equipment_inventory:
            return {"error": "Equipment not found"}
        
        equipment = self.equipment_inventory[asset_id]
        location_history = self.location_history.get(asset_id, [])
        utilization = self.utilization_metrics.get(asset_id, 0.0)
        
        return {
            "equipment": equipment.to_dict(),
            "location_history": location_history,
            "utilization": utilization,
            "last_seen": datetime.utcnow().isoformat()
        }
    
    async def request_equipment(self, equipment_type: str, unit_id: str, priority: str = "normal") -> Dict[str, Any]:
        """Request equipment allocation"""
        message = AgentMessage(
            id=f"equipment_request_{datetime.utcnow().isoformat()}",
            sender_id="api",
            recipient_id=self.agent_id,
            message_type="equipment_allocation_request",
            content={
                "equipment_type": equipment_type,
                "unit_id": unit_id,
                "priority": priority,
                "requester_id": "api"
            }
        )
        
        response = await self._handle_allocation_request(message.content)
        return response.content if response else {"error": "Failed to process request"}
    
    async def tick(self):
        """Periodic equipment tracking tasks"""
        try:
            # Check maintenance schedules
            await self._check_maintenance_schedules()
            
            # Optimize equipment distribution
            await self._optimize_equipment_distribution()
            
            # Update performance metrics
            await self._update_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Error in equipment tracking tick: {e}")
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make equipment-related decisions"""
        decision_type = context.get("decision_type")
        
        if decision_type == "equipment_allocation":
            return await self._decide_equipment_allocation(context)
        elif decision_type == "maintenance_scheduling":
            return await self._decide_maintenance_schedule(context)
        elif decision_type == "equipment_redistribution":
            return await self._decide_equipment_redistribution(context)
        else:
            raise ValueError(f"Unknown decision type: {decision_type}")
    
    async def _handle_location_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle equipment location updates from RTLS"""
        asset_id = data["asset_id"]
        location = data["location"]
        timestamp = data.get("timestamp", datetime.utcnow())
        
        # Update equipment location
        if asset_id in self.equipment_inventory:
            self.equipment_inventory[asset_id]["location"] = location
            self.equipment_inventory[asset_id]["last_seen"] = timestamp
            
            # Track location history
            if asset_id not in self.location_history:
                self.location_history[asset_id] = []
            self.location_history[asset_id].append({
                "location": location,
                "timestamp": timestamp
            })
            
            # Keep only recent history
            cutoff = timestamp - timedelta(days=7)
            self.location_history[asset_id] = [
                entry for entry in self.location_history[asset_id]
                if entry["timestamp"] > cutoff
            ]
        
        return {"success": True, "asset_id": asset_id, "location": location}
    
    async def _handle_allocation_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle equipment allocation requests"""
        equipment_type = data["equipment_type"]
        unit_id = data["unit_id"]
        priority = data.get("priority", "normal")
        
        # Find available equipment
        available_equipment = await self._find_available_equipment(
            equipment_type, unit_id, priority
        )
        
        if available_equipment:
            # Reserve the equipment
            equipment_id = available_equipment["asset_id"]
            await self._reserve_equipment(equipment_id, unit_id)
            
            return {
                "success": True,
                "equipment": available_equipment,
                "estimated_delivery_time": 15  # minutes
            }
        else:
            # No equipment available
            alternatives = await self._suggest_equipment_alternatives(
                equipment_type, unit_id
            )
            
            return {
                "success": False,
                "reason": "no_equipment_available",
                "alternatives": alternatives,
                "estimated_wait_time": await self._estimate_equipment_wait_time(equipment_type)
            }
    
    async def _find_available_equipment(
        self, equipment_type: str, unit_id: str, priority: str
    ) -> Optional[Dict[str, Any]]:
        """Find available equipment of specified type"""
        
        available_items = []
        for asset_id, equipment in self.equipment_inventory.items():
            if (equipment.get("type") == equipment_type and 
                equipment.get("status") == "available"):
                
                # Calculate suitability score
                score = await self._calculate_equipment_suitability(
                    equipment, unit_id, priority
                )
                available_items.append((equipment, score))
        
        if available_items:
            # Return the best match
            best_equipment, _ = max(available_items, key=lambda x: x[1])
            return best_equipment
        
        return None
    
    async def _calculate_equipment_suitability(
        self, equipment: Dict[str, Any], unit_id: str, priority: str
    ) -> float:
        """Calculate suitability score for equipment assignment"""
        score = 0.0
        
        # Distance factor (closer is better)
        current_location = equipment.get("location", {})
        distance_score = await self._calculate_distance_score(current_location, unit_id)
        score += distance_score * 0.4
        
        # Condition factor
        condition = equipment.get("condition_score", 1.0)
        score += condition * 0.3
        
        # Utilization factor (less used is better for maintenance)
        utilization = self.utilization_metrics.get(equipment["asset_id"], 0.0)
        utilization_score = 1.0 - utilization
        score += utilization_score * 0.2
        
        # Priority factor
        if priority == "urgent":
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    async def _analyze_utilization(self) -> None:
        """Analyze equipment utilization patterns"""
        if not self.utilization_analyzer:
            return
        
        # Prepare usage data
        usage_data = []
        for asset_id, equipment in self.equipment_inventory.items():
            usage_data.append({
                "asset_id": asset_id,
                "utilization": self.utilization_metrics.get(asset_id, 0.0),
                "equipment_type": equipment.get("type", "unknown"),
                "location": equipment.get("location", {})
            })
        
        # Analyze patterns
        analysis = await self.utilization_analyzer.analyze_patterns(usage_data)
        
        # Check for optimization opportunities
        if analysis.get("average_utilization", 0) < self.config["utilization_threshold"]:
            await self._send_utilization_alert(analysis)
    
    async def _check_maintenance_schedules(self) -> None:
        """Check equipment maintenance schedules"""
        if not self.maintenance_predictor:
            return
        
        current_time = datetime.utcnow()
        
        for asset_id, equipment in self.equipment_inventory.items():
            # Check if maintenance is due
            last_maintenance = equipment.get("last_maintenance", current_time - timedelta(days=365))
            days_since_maintenance = (current_time - last_maintenance).days
            
            # Predict maintenance needs
            prediction = await self.maintenance_predictor.predict({
                "usage_hours": equipment.get("usage_hours", 0),
                "days_since_maintenance": days_since_maintenance,
                "equipment_age": equipment.get("age_months", 0)
            })
            
            if prediction["needs_maintenance"]:
                await self._schedule_maintenance(asset_id, prediction)
    
    async def _optimize_equipment_distribution(self) -> None:
        """Optimize equipment distribution across units"""
        # Analyze current distribution
        distribution_analysis = await self._analyze_current_distribution()
        
        # Identify optimization opportunities
        if distribution_analysis.get("needs_optimization", False):
            recommendations = await self._generate_redistribution_recommendations()
            
            # Send recommendations to operations team
            await self._send_redistribution_recommendations(recommendations)
    
    async def _load_equipment_inventory(self) -> None:
        """Load current equipment inventory"""
        # Mock equipment inventory - in real system, load from database
        self.equipment_inventory = {
            "EQ_001": {
                "asset_id": "EQ_001",
                "type": "iv_pump",
                "status": "available",
                "location": {"unit": "ICU_01", "room": "101"},
                "condition_score": 0.9,
                "usage_hours": 2500,
                "last_maintenance": datetime.utcnow() - timedelta(days=30)
            },
            "EQ_002": {
                "asset_id": "EQ_002", 
                "type": "wheelchair",
                "status": "in_use",
                "location": {"unit": "MED_01", "room": "205"},
                "condition_score": 0.8,
                "usage_hours": 1200,
                "last_maintenance": datetime.utcnow() - timedelta(days=60)
            }
        }
        
        # Initialize utilization metrics
        for asset_id in self.equipment_inventory:
            self.utilization_metrics[asset_id] = 0.7  # Mock utilization
    
    async def _initialize_tracking_systems(self) -> None:
        """Initialize RTLS and other tracking systems"""
        # In real implementation, this would:
        # - Connect to RTLS system
        # - Set up IoT device connections
        # - Initialize sensor data streams
        pass
    
    async def _update_equipment_locations(self) -> None:
        """Update equipment locations from tracking systems"""
        # Mock location updates
        pass
    
    async def _update_performance_metrics(self) -> None:
        """Update agent performance metrics"""
        if self.utilization_metrics:
            self.average_utilization = sum(self.utilization_metrics.values()) / len(self.utilization_metrics)
        
        # Calculate maintenance compliance
        total_equipment = len(self.equipment_inventory)
        compliant_equipment = sum(
            1 for eq in self.equipment_inventory.values()
            if (datetime.utcnow() - eq.get("last_maintenance", datetime.utcnow())).days < 90
        )
        self.maintenance_compliance = compliant_equipment / total_equipment if total_equipment > 0 else 0.0
    
    async def _handle_maintenance_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle equipment maintenance requests"""
        asset_id = data["asset_id"]
        maintenance_type = data.get("maintenance_type", "routine")
        urgency = data.get("urgency", "normal")
        
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            
            # Schedule maintenance
            maintenance_id = f"maint_{asset_id}_{datetime.utcnow().isoformat()}"
            maintenance_data = {
                "maintenance_id": maintenance_id,
                "asset_id": asset_id,
                "type": maintenance_type,
                "urgency": urgency,
                "scheduled_date": datetime.utcnow() + timedelta(days=1),
                "status": "scheduled"
            }
            
            # Update equipment status
            equipment["status"] = "maintenance_scheduled"
            equipment["next_maintenance"] = maintenance_data["scheduled_date"]
            
            return {"success": True, "maintenance": maintenance_data}
        
        return {"success": False, "error": "Equipment not found"}
    
    async def _handle_usage_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle equipment usage updates"""
        asset_id = data["asset_id"]
        usage_hours = data.get("usage_hours", 0)
        utilization_rate = data.get("utilization_rate", 0.0)
        
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            equipment["usage_hours"] = equipment.get("usage_hours", 0) + usage_hours
            equipment["last_used"] = datetime.utcnow()
            
            # Update utilization metrics
            self.utilization_metrics[asset_id] = utilization_rate
            
            return {"success": True, "updated_usage": equipment["usage_hours"]}
        
        return {"success": False, "error": "Equipment not found"}
    
    async def _handle_equipment_reservation(self, payload: Dict[str, Any]) -> None:
        """Handle equipment reservation requests"""
        asset_id = payload.get("asset_id")
        reserved_by = payload.get("reserved_by")
        duration = payload.get("duration_minutes", 60)
        
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            if equipment["status"] == "available":
                equipment["status"] = "reserved"
                equipment["reserved_by"] = reserved_by
                equipment["reservation_expires"] = datetime.utcnow() + timedelta(minutes=duration)
                
                self.logger.info(f"Equipment {asset_id} reserved by {reserved_by}")
    
    async def _handle_equipment_release(self, payload: Dict[str, Any]) -> None:
        """Handle equipment release requests"""
        asset_id = payload.get("asset_id")
        
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            equipment["status"] = "available"
            equipment.pop("reserved_by", None)
            equipment.pop("reservation_expires", None)
            
            self.logger.info(f"Equipment {asset_id} released and available")
    
    async def _respond_equipment_availability(self, payload: Dict[str, Any], sender_agent: str) -> None:
        """Respond to equipment availability requests"""
        equipment_type = payload.get("equipment_type")
        location = payload.get("location")
        
        available_equipment = []
        for asset_id, equipment in self.equipment_inventory.items():
            if (equipment.get("type") == equipment_type and 
                equipment.get("status") == "available"):
                
                # Check location proximity if specified
                if location:
                    distance_score = await self._calculate_distance_score(
                        equipment.get("location", {}), location
                    )
                    if distance_score > 0.5:  # Close enough
                        available_equipment.append({
                            "asset_id": asset_id,
                            "location": equipment["location"],
                            "condition_score": equipment.get("condition_score", 1.0),
                            "distance_score": distance_score
                        })
                else:
                    available_equipment.append({
                        "asset_id": asset_id,
                        "location": equipment["location"],
                        "condition_score": equipment.get("condition_score", 1.0)
                    })
        
        # Send response back to requesting agent
        response_message = AgentMessage(
            message_id=f"availability_response_{datetime.utcnow().isoformat()}",
            sender_agent=self.agent_id,
            recipient_agent=sender_agent,
            message_type="equipment_availability_response",
            payload={
                "equipment_type": equipment_type,
                "available_equipment": available_equipment,
                "total_available": len(available_equipment)
            }
        )
        
        await self._send_message(response_message)
    
    async def _calculate_distance_score(self, location1: Dict[str, Any], location2: Any) -> float:
        """Calculate distance score between two locations"""
        # Simplified distance calculation
        # In real system, this would use actual facility mapping
        
        if isinstance(location2, str):
            location2 = {"unit": location2}
        elif isinstance(location2, dict):
            pass
        else:
            return 0.5  # Default score
        
        unit1 = location1.get("unit", "")
        unit2 = location2.get("unit", "")
        
        if unit1 == unit2:
            return 1.0  # Same unit, very close
        elif unit1 and unit2:
            # Different units, calculate approximate distance
            return 0.7  # Moderate distance
        else:
            return 0.3  # Unknown distance
    
    async def _reserve_equipment(self, equipment_id: str, unit_id: str) -> None:
        """Reserve equipment for a specific unit"""
        if equipment_id in self.equipment_inventory:
            equipment = self.equipment_inventory[equipment_id]
            equipment["status"] = "reserved"
            equipment["reserved_for"] = unit_id
            equipment["reservation_time"] = datetime.utcnow()
    
    async def _suggest_equipment_alternatives(
        self, equipment_type: str, unit_id: str
    ) -> List[Dict[str, Any]]:
        """Suggest alternative equipment options"""
        alternatives = []
        
        # Look for similar equipment types
        similar_types = self._get_similar_equipment_types(equipment_type)
        
        for alt_type in similar_types:
            alt_equipment = await self._find_available_equipment(alt_type, unit_id, "normal")
            if alt_equipment:
                alternatives.append({
                    "equipment_type": alt_type,
                    "equipment": alt_equipment,
                    "similarity_score": 0.8
                })
        
        return alternatives
    
    def _get_similar_equipment_types(self, equipment_type: str) -> List[str]:
        """Get similar equipment types for alternatives"""
        similarity_map = {
            "iv_pump": ["syringe_pump", "infusion_pump"],
            "wheelchair": ["transport_chair", "walker"],
            "ventilator": ["bipap", "cpap"],
            "monitor": ["portable_monitor", "telemetry"]
        }
        
        return similarity_map.get(equipment_type, [])
    
    async def _estimate_equipment_wait_time(self, equipment_type: str) -> int:
        """Estimate wait time for equipment to become available"""
        # Check when current equipment of this type will be available
        min_wait_time = 999999  # Very large number
        
        for equipment in self.equipment_inventory.values():
            if equipment.get("type") == equipment_type:
                if equipment.get("status") == "in_use":
                    # Estimate based on typical usage duration
                    estimated_release = datetime.utcnow() + timedelta(hours=2)
                    wait_minutes = (estimated_release - datetime.utcnow()).total_seconds() / 60
                    min_wait_time = min(min_wait_time, wait_minutes)
                elif equipment.get("status") == "maintenance":
                    # Estimate maintenance completion
                    wait_minutes = 240  # 4 hours typical maintenance
                    min_wait_time = min(min_wait_time, wait_minutes)
        
        return int(min_wait_time) if min_wait_time < 999999 else 180  # Default 3 hours
    
    async def _send_utilization_alert(self, analysis: Dict[str, Any]) -> None:
        """Send utilization alert to operations team"""
        alert_message = AgentMessage(
            message_id=f"utilization_alert_{datetime.utcnow().isoformat()}",
            sender_agent=self.agent_id,
            recipient_agent="operations_manager",
            message_type="utilization_alert",
            payload={
                "alert_type": "low_utilization",
                "average_utilization": analysis.get("average_utilization", 0),
                "threshold": self.config["utilization_threshold"],
                "recommendations": analysis.get("recommendations", [])
            }
        )
        
        await self._send_message(alert_message)
    
    async def _schedule_maintenance(self, asset_id: str, prediction: Dict[str, Any]) -> None:
        """Schedule equipment maintenance"""
        maintenance_urgency = "high" if prediction.get("urgency_score", 0) > 0.8 else "normal"
        
        maintenance_request = {
            "asset_id": asset_id,
            "maintenance_type": prediction.get("maintenance_type", "routine"),
            "urgency": maintenance_urgency,
            "predicted_failure_date": prediction.get("predicted_failure_date"),
            "recommended_date": datetime.utcnow() + timedelta(days=3)
        }
        
        # Update equipment status
        if asset_id in self.equipment_inventory:
            self.equipment_inventory[asset_id]["maintenance_scheduled"] = True
            self.equipment_inventory[asset_id]["maintenance_request"] = maintenance_request
        
        self.logger.info(f"Scheduled maintenance for equipment {asset_id}")
    
    async def _analyze_current_distribution(self) -> Dict[str, Any]:
        """Analyze current equipment distribution"""
        distribution = {}
        
        for equipment in self.equipment_inventory.values():
            unit = equipment.get("location", {}).get("unit", "unknown")
            equipment_type = equipment.get("type", "unknown")
            
            if unit not in distribution:
                distribution[unit] = {}
            
            if equipment_type not in distribution[unit]:
                distribution[unit][equipment_type] = 0
            
            distribution[unit][equipment_type] += 1
        
        # Analyze for imbalances
        total_units = len(distribution)
        needs_optimization = False
        
        for unit_dist in distribution.values():
            for equipment_type, count in unit_dist.items():
                avg_per_unit = sum(
                    d.get(equipment_type, 0) for d in distribution.values()
                ) / total_units
                
                if abs(count - avg_per_unit) > avg_per_unit * 0.5:  # 50% deviation
                    needs_optimization = True
                    break
        
        return {
            "distribution": distribution,
            "needs_optimization": needs_optimization,
            "total_units": total_units
        }
    
    async def _generate_redistribution_recommendations(self) -> List[Dict[str, Any]]:
        """Generate equipment redistribution recommendations"""
        recommendations = []
        distribution_analysis = await self._analyze_current_distribution()
        distribution = distribution_analysis["distribution"]
        
        # Simple redistribution logic
        for equipment_type in ["iv_pump", "wheelchair", "monitor"]:
            type_distribution = []
            
            for unit, unit_dist in distribution.items():
                count = unit_dist.get(equipment_type, 0)
                type_distribution.append((unit, count))
            
            # Sort by count
            type_distribution.sort(key=lambda x: x[1])
            
            # If there's significant imbalance, recommend redistribution
            if len(type_distribution) >= 2:
                lowest_unit, lowest_count = type_distribution[0]
                highest_unit, highest_count = type_distribution[-1]
                
                if highest_count - lowest_count > 2:
                    recommendations.append({
                        "action": "redistribute",
                        "equipment_type": equipment_type,
                        "from_unit": highest_unit,
                        "to_unit": lowest_unit,
                        "quantity": (highest_count - lowest_count) // 2,
                        "priority": "medium"
                    })
        
        return recommendations
    
    async def _send_redistribution_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """Send redistribution recommendations to operations team"""
        if recommendations:
            message = AgentMessage(
                message_id=f"redistribution_rec_{datetime.utcnow().isoformat()}",
                sender_agent=self.agent_id,
                recipient_agent="operations_manager",
                message_type="redistribution_recommendations",
                payload={
                    "recommendations": recommendations,
                    "total_recommendations": len(recommendations),
                    "potential_efficiency_gain": 0.15
                }
            )
            
            await self._send_message(message)
    
    async def _decide_equipment_allocation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make equipment allocation decisions"""
        equipment_type = context.get("equipment_type")
        requesting_unit = context.get("unit_id")
        priority = context.get("priority", "normal")
        
        # Find best equipment option
        available_equipment = await self._find_available_equipment(
            equipment_type, requesting_unit, priority
        )
        
        if available_equipment:
            decision = {
                "action": "allocate",
                "equipment": available_equipment,
                "confidence": 0.9,
                "rationale": "Suitable equipment available with good condition score"
            }
        else:
            decision = {
                "action": "wait",
                "estimated_wait_time": await self._estimate_equipment_wait_time(equipment_type),
                "alternatives": await self._suggest_equipment_alternatives(equipment_type, requesting_unit),
                "confidence": 0.7,
                "rationale": "No immediate availability, alternatives suggested"
            }
        
        return decision
    
    async def _decide_maintenance_schedule(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make maintenance scheduling decisions"""
        asset_id = context.get("asset_id")
        urgency = context.get("urgency", "normal")
        current_usage = context.get("current_usage", "normal")
        
        if urgency == "critical":
            schedule_date = datetime.utcnow() + timedelta(hours=4)
            confidence = 0.95
        elif urgency == "high":
            schedule_date = datetime.utcnow() + timedelta(days=1)
            confidence = 0.85
        else:
            schedule_date = datetime.utcnow() + timedelta(days=7)
            confidence = 0.75
        
        return {
            "action": "schedule_maintenance",
            "asset_id": asset_id,
            "scheduled_date": schedule_date.isoformat(),
            "urgency": urgency,
            "confidence": confidence,
            "maintenance_window_hours": 4
        }
    
    async def _decide_equipment_redistribution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make equipment redistribution decisions"""
        current_distribution = await self._analyze_current_distribution()
        
        if current_distribution.get("needs_optimization", False):
            recommendations = await self._generate_redistribution_recommendations()
            
            return {
                "action": "redistribute",
                "recommendations": recommendations,
                "confidence": 0.8,
                "expected_efficiency_improvement": 0.15,
                "implementation_timeline": "within_24_hours"
            }
        else:
            return {
                "action": "maintain_current",
                "rationale": "Current distribution is optimal",
                "confidence": 0.9
            }
    
    # API Methods for external access
    async def get_equipment_status(self) -> Dict[str, Any]:
        """Get overall equipment status"""
        total_equipment = len(self.equipment_inventory)
        available_count = len([eq for eq in self.equipment_inventory.values() if eq.get("status") == "available"])
        in_use_count = len([eq for eq in self.equipment_inventory.values() if eq.get("status") == "in_use"])
        maintenance_count = len([eq for eq in self.equipment_inventory.values() if "maintenance" in eq.get("status", "")])
        
        return {
            "total_equipment": total_equipment,
            "available": available_count,
            "in_use": in_use_count,
            "in_maintenance": maintenance_count,
            "average_utilization": self.average_utilization,
            "tracking_accuracy": self.tracking_accuracy,
            "maintenance_compliance": self.maintenance_compliance
        }
    
    async def get_all_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment information"""
        return list(self.equipment_inventory.values())
    
    async def track_equipment(self, asset_id: str) -> Dict[str, Any]:
        """Track specific equipment"""
        if asset_id in self.equipment_inventory:
            equipment = self.equipment_inventory[asset_id]
            location_history = self.location_history.get(asset_id, [])
            
            return {
                "equipment": equipment,
                "location_history": location_history[-10:],  # Last 10 locations
                "utilization": self.utilization_metrics.get(asset_id, 0.0)
            }
        else:
            return {"error": "Equipment not found"}
    
    async def request_equipment(self, equipment_type: str, unit_id: str, priority: str = "normal") -> Dict[str, Any]:
        """Request equipment allocation"""
        allocation_result = await self._handle_allocation_request({
            "equipment_type": equipment_type,
            "unit_id": unit_id,
            "priority": priority
        })
        
        return allocation_result
