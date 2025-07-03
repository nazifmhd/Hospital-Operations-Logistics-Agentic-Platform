"""
Bed Management Agent for optimizing bed allocation and patient flow
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from src.core.base_agent import BaseAgent, AgentEvent, AgentMessage
from src.models.bed_models import BedResponse, PatientAdmission, BedAssignment
from src.utils.prediction_models import LSTMPredictor, AllocationOptimizer


class BedManagementAgent(BaseAgent):
    """Agent responsible for bed management and patient flow optimization"""
    
    def __init__(self):
        super().__init__(
            agent_id="bed_management_agent",
            agent_type="bed_management",
            description="Manages bed allocation, predicts availability, and optimizes patient flow",
            config={
                "prediction_horizon_hours": 24,
                "optimization_interval_minutes": 15,
                "alert_threshold_availability": 0.05,  # 5% availability
                "tick_interval": 30.0  # 30 seconds
            }
        )
        
        # Prediction and optimization models
        self.demand_predictor: Optional[LSTMPredictor] = None
        self.allocation_optimizer: Optional[AllocationOptimizer] = None
        
        # Current state
        self.current_bed_status: Dict[str, BedResponse] = {}
        self.pending_admissions: List[PatientAdmission] = []
        self.recent_assignments: List[BedAssignment] = []
        
        # Performance tracking
        self.prediction_accuracy = 0.0
        self.average_wait_time = 0.0
        self.bed_utilization_rate = 0.0
    
    async def _initialize_agent(self) -> None:
        """Initialize bed management specific resources"""
        self.logger.info("Initializing Bed Management Agent")
        
        # Initialize ML models
        self.demand_predictor = LSTMPredictor(
            sequence_length=24,  # 24 hours of data
            features=['bed_demand', 'admissions', 'discharges', 'transfers']
        )
        
        self.allocation_optimizer = AllocationOptimizer(
            objectives=['minimize_wait_time', 'maximize_utilization', 'minimize_transfers'],
            constraints=['isolation_requirements', 'equipment_needs', 'nurse_ratios']
        )
        
        # Load historical data and train models
        await self._load_historical_data()
        await self._train_prediction_models()
        
        # Initialize current bed status
        await self._refresh_bed_status()
        
        self.logger.info("Bed Management Agent initialized successfully")
    
    async def _cleanup_agent(self) -> None:
        """Cleanup bed management resources"""
        self.logger.info("Cleaning up Bed Management Agent")
        # Save model states, close connections, etc.
    
    async def _process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process bed management related events"""
        event_type = event.event_type
        data = event.data
        
        self.logger.debug(f"Processing event: {event_type}")
        
        if event_type == "patient_admission_request":
            return await self._handle_admission_request(data)
        
        elif event_type == "patient_discharge":
            return await self._handle_patient_discharge(data)
        
        elif event_type == "bed_status_update":
            return await self._handle_bed_status_update(data)
        
        elif event_type == "emergency_admission":
            return await self._handle_emergency_admission(data)
        
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
            return None
    
    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle messages from other agents"""
        message_type = message.message_type
        payload = message.payload
        
        if message_type == "staff_availability_update":
            await self._update_staffing_constraints(payload)
        
        elif message_type == "equipment_availability_update":
            await self._update_equipment_constraints(payload)
        
        elif message_type == "supply_shortage_alert":
            await self._handle_supply_shortage(payload)
        
        else:
            self.logger.debug(f"Unhandled message type: {message_type}")
    
    async def _agent_tick(self) -> None:
        """Perform regular bed management tasks"""
        try:
            # Update bed status
            await self._refresh_bed_status()
            
            # Check for optimization opportunities
            if await self._should_optimize():
                await self._optimize_bed_allocation()
            
            # Update predictions
            await self._update_demand_predictions()
            
            # Check for alerts
            await self._check_availability_alerts()
            
            # Update metrics
            await self._update_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Error in bed management tick: {e}")
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make bed allocation decisions"""
        decision_type = context.get("decision_type")
        
        if decision_type == "bed_assignment":
            return await self._decide_bed_assignment(context)
        
        elif decision_type == "discharge_planning":
            return await self._decide_discharge_timing(context)
        
        elif decision_type == "capacity_expansion":
            return await self._decide_capacity_expansion(context)
        
        else:
            raise ValueError(f"Unknown decision type: {decision_type}")
    
    async def _handle_admission_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle patient admission request"""
        patient_id = data["patient_id"]
        acuity_score = data.get("acuity_score", 1.0)
        isolation_requirements = data.get("isolation_requirements", [])
        equipment_needs = data.get("equipment_needs", [])
        preferred_unit = data.get("preferred_unit")
        
        # Create patient admission record
        admission = PatientAdmission(
            patient_id=patient_id,
            admission_timestamp=datetime.utcnow(),
            acuity_score=acuity_score,
            isolation_requirements=isolation_requirements,
            equipment_needs=equipment_needs,
            preferred_unit=preferred_unit
        )
        
        # Find optimal bed assignment
        assignment = await self._find_optimal_bed(admission)
        
        if assignment:
            # Coordinate with other agents
            coordination_result = await self._coordinate_admission(assignment)
            
            if coordination_result["success"]:
                self.recent_assignments.append(assignment)
                await self._notify_assignment(assignment)
                
                return {
                    "success": True,
                    "assignment": assignment.dict(),
                    "estimated_wait_time": assignment.estimated_wait_time
                }
            else:
                # Handle coordination failure
                return {
                    "success": False,
                    "reason": "coordination_failed",
                    "details": coordination_result["reason"]
                }
        else:
            # No suitable bed available
            self.pending_admissions.append(admission)
            estimated_wait = await self._estimate_wait_time(admission)
            
            return {
                "success": False,
                "reason": "no_beds_available",
                "estimated_wait_time": estimated_wait,
                "alternatives": await self._suggest_alternatives(admission)
            }
    
    async def _find_optimal_bed(self, admission: PatientAdmission) -> Optional[BedAssignment]:
        """Find the optimal bed for a patient admission"""
        available_beds = [
            bed for bed in self.current_bed_status.values()
            if bed.status == "available"
        ]
        
        if not available_beds:
            return None
        
        # Use optimization algorithm to find best bed
        optimal_bed = await self.allocation_optimizer.optimize(
            patient=admission,
            available_beds=available_beds,
            current_assignments=self.recent_assignments
        )
        
        if optimal_bed:
            return BedAssignment(
                patient_id=admission.patient_id,
                bed_id=optimal_bed.bed_id,
                unit_id=optimal_bed.unit_id,
                assignment_timestamp=datetime.utcnow(),
                estimated_wait_time=0,  # Available immediately
                assignment_score=optimal_bed.suitability_score
            )
        
        return None
    
    async def _coordinate_admission(self, assignment: BedAssignment) -> Dict[str, Any]:
        """Coordinate with other agents for admission"""
        coordination_tasks = []
        
        # Check with staff allocation agent
        staff_message = AgentMessage(
            sender_agent=self.agent_id,
            receiver_agent="staff_allocation_agent",
            message_type="check_staffing_capacity",
            payload={
                "unit_id": assignment.unit_id,
                "admission_time": assignment.assignment_timestamp.isoformat(),
                "patient_acuity": assignment.patient_acuity_score
            }
        )
        coordination_tasks.append(self.send_message(staff_message))
        
        # Check with equipment tracker agent
        equipment_message = AgentMessage(
            sender_agent=self.agent_id,
            receiver_agent="equipment_tracker_agent",
            message_type="reserve_equipment",
            payload={
                "bed_id": assignment.bed_id,
                "equipment_needs": assignment.equipment_requirements
            }
        )
        coordination_tasks.append(self.send_message(equipment_message))
        
        # Wait for coordination responses
        try:
            await asyncio.gather(*coordination_tasks, timeout=10.0)
            return {"success": True}
        except asyncio.TimeoutError:
            return {"success": False, "reason": "coordination_timeout"}
        except Exception as e:
            return {"success": False, "reason": f"coordination_error: {str(e)}"}
    
    async def _predict_bed_demand(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Predict bed demand for the next N hours"""
        if not self.demand_predictor:
            return {"error": "Prediction model not initialized"}
        
        # Prepare input features
        current_features = await self._get_current_features()
        
        # Make prediction
        prediction = await self.demand_predictor.predict(
            features=current_features,
            horizon=hours_ahead
        )
        
        return {
            "prediction_horizon_hours": hours_ahead,
            "predicted_demand": prediction["demand"],
            "confidence_interval": prediction["confidence"],
            "peak_hours": prediction["peak_periods"],
            "low_demand_hours": prediction["low_periods"]
        }
    
    async def _optimize_bed_allocation(self) -> None:
        """Optimize current bed allocation"""
        if not self.pending_admissions:
            return
        
        self.logger.info("Optimizing bed allocation for pending admissions")
        
        # Get current available beds
        available_beds = [
            bed for bed in self.current_bed_status.values()
            if bed.status == "available"
        ]
        
        # Optimize assignments for all pending admissions
        optimized_assignments = await self.allocation_optimizer.batch_optimize(
            patients=self.pending_admissions,
            available_beds=available_beds
        )
        
        # Process optimized assignments
        for assignment in optimized_assignments:
            if assignment.score > 0.7:  # Good assignment threshold
                coordination_result = await self._coordinate_admission(assignment)
                
                if coordination_result["success"]:
                    # Remove from pending
                    self.pending_admissions = [
                        p for p in self.pending_admissions
                        if p.patient_id != assignment.patient_id
                    ]
                    
                    self.recent_assignments.append(assignment)
                    await self._notify_assignment(assignment)
    
    async def _check_availability_alerts(self) -> None:
        """Check for low bed availability and send alerts"""
        total_beds = len(self.current_bed_status)
        available_beds = sum(
            1 for bed in self.current_bed_status.values()
            if bed.status == "available"
        )
        
        availability_rate = available_beds / total_beds if total_beds > 0 else 0
        
        if availability_rate < self.config["alert_threshold_availability"]:
            alert_message = AgentMessage(
                sender_agent=self.agent_id,
                receiver_agent=None,  # Broadcast
                message_type="critical_bed_shortage_alert",
                payload={
                    "availability_rate": availability_rate,
                    "available_beds": available_beds,
                    "total_beds": total_beds,
                    "pending_admissions": len(self.pending_admissions),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await self.send_message(alert_message)
            self.logger.warning(f"Critical bed shortage: {availability_rate:.1%} availability")
    
    async def _refresh_bed_status(self) -> None:
        """Refresh current bed status from database"""
        # This would typically query the database
        # For now, we'll simulate some bed statuses
        pass
    
    async def _load_historical_data(self) -> None:
        """Load historical data for model training"""
        # Load historical bed utilization, admission patterns, etc.
        pass
    
    async def _train_prediction_models(self) -> None:
        """Train prediction models with historical data"""
        # Train LSTM model for demand prediction
        # Train optimization models
        pass
    
    async def _should_optimize(self) -> bool:
        """Determine if optimization should be performed"""
        # Check if enough time has passed since last optimization
        # Check if there are pending admissions
        # Check if bed status has changed significantly
        return len(self.pending_admissions) > 0
    
    async def _update_demand_predictions(self) -> None:
        """Update demand predictions with latest data"""
        pass
    
    async def _update_performance_metrics(self) -> None:
        """Update agent performance metrics"""
        # Calculate bed utilization rate
        if self.current_bed_status:
            occupied_beds = sum(
                1 for bed in self.current_bed_status.values()
                if bed.status == "occupied"
            )
            self.bed_utilization_rate = occupied_beds / len(self.current_bed_status)
        
        # Calculate average wait time from recent assignments
        if self.recent_assignments:
            wait_times = [a.estimated_wait_time for a in self.recent_assignments[-10:]]
            self.average_wait_time = sum(wait_times) / len(wait_times)
    
    async def _get_current_features(self) -> Dict[str, float]:
        """Get current features for prediction"""
        return {
            "current_occupancy": self.bed_utilization_rate,
            "pending_admissions": len(self.pending_admissions),
            "hour_of_day": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday()
        }
    
    async def _notify_assignment(self, assignment: BedAssignment) -> None:
        """Notify relevant systems about bed assignment"""
        # Send notification to EMR, nursing stations, etc.
        pass
