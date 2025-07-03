"""
Agent orchestrator for coordinating multiple hospital operation agents
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.base_agent import BaseAgent, AgentMessage, AgentEvent
from src.agents.bed_management_agent import BedManagementAgent
from src.agents.equipment_tracker_agent import EquipmentTrackerAgent
from src.agents.staff_allocation_agent import StaffAllocationAgent
from src.agents.supply_inventory_agent import SupplyInventoryAgent


class AgentOrchestrator:
    """Central coordinator for all hospital operation agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("agent_orchestrator")
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        # Performance tracking
        self.messages_processed = 0
        self.coordination_events = 0
        self.start_time: Optional[datetime] = None
    
    async def initialize(self) -> None:
        """Initialize the orchestrator and all agents"""
        self.logger.info("Initializing Agent Orchestrator")
        
        try:
            # Initialize agents
            await self._initialize_agents()
            
            # Start message processing
            self.running = True
            self.start_time = datetime.utcnow()
            
            # Start the coordination loop
            asyncio.create_task(self._coordination_loop())
            
            self.logger.info("Agent Orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the orchestrator and all agents"""
        self.logger.info("Shutting down Agent Orchestrator")
        
        self.running = False
        
        # Stop all agents
        for agent in self.agents.values():
            try:
                await agent.stop()
            except Exception as e:
                self.logger.error(f"Error stopping agent {agent.agent_id}: {e}")
        
        self.logger.info("Agent Orchestrator shutdown completed")
    
    async def _initialize_agents(self) -> None:
        """Initialize all agent instances"""
        # Initialize Bed Management Agent
        bed_agent = BedManagementAgent()
        await self._register_agent(bed_agent)
        
        # Initialize Equipment Tracker Agent
        equipment_agent = EquipmentTrackerAgent()
        await self._register_agent(equipment_agent)
        
        # Initialize Staff Allocation Agent
        staff_agent = StaffAllocationAgent()
        await self._register_agent(staff_agent)
        
        # Initialize Supply Inventory Agent
        supply_agent = SupplyInventoryAgent()
        await self._register_agent(supply_agent)
        # await self._register_agent(supply_agent)
    
    async def _register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator"""
        self.logger.info(f"Registering agent: {agent.agent_id}")
        
        # Set up message handling
        original_send_message = agent.send_message
        agent.send_message = lambda msg: self._route_message(msg)
        
        # Initialize and start the agent
        await agent.initialize()
        self.agents[agent.agent_id] = agent
        
        # Start agent in background
        asyncio.create_task(agent.start())
        
        self.logger.info(f"Agent {agent.agent_id} registered and started")
    
    async def _coordination_loop(self) -> None:
        """Main coordination loop for processing messages and events"""
        while self.running:
            try:
                # Process pending messages
                await self._process_pending_messages()
                
                # Perform coordination tasks
                await self._perform_coordination()
                
                # Brief pause to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(1.0)  # Backoff on error
    
    async def _process_pending_messages(self) -> None:
        """Process all pending inter-agent messages"""
        while True:
            try:
                # Get message with short timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=0.1
                )
                
                await self._deliver_message(message)
                self.messages_processed += 1
                
            except asyncio.TimeoutError:
                # No messages pending
                break
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _route_message(self, message: AgentMessage) -> None:
        """Route a message between agents"""
        await self.message_queue.put(message)
    
    async def _deliver_message(self, message: AgentMessage) -> None:
        """Deliver a message to the target agent(s)"""
        if message.receiver_agent is None:
            # Broadcast message to all agents except sender
            for agent_id, agent in self.agents.items():
                if agent_id != message.sender_agent:
                    await agent.receive_message(message)
        else:
            # Send to specific agent
            target_agent = self.agents.get(message.receiver_agent)
            if target_agent:
                await target_agent.receive_message(message)
            else:
                self.logger.warning(f"Target agent not found: {message.receiver_agent}")
    
    async def _perform_coordination(self) -> None:
        """Perform system-wide coordination tasks"""
        # Monitor agent health
        await self._monitor_agent_health()
        
        # Resolve conflicts if any
        await self._resolve_conflicts()
        
        # Update system metrics
        await self._update_system_metrics()
    
    async def _monitor_agent_health(self) -> None:
        """Monitor the health and status of all agents"""
        for agent_id, agent in self.agents.items():
            try:
                status = agent.get_status()
                
                if status["status"] == "error":
                    self.logger.warning(f"Agent {agent_id} in error state")
                    # Could implement recovery logic here
                
                # Check if agent is responsive
                # Could ping agent or check last activity
                
            except Exception as e:
                self.logger.error(f"Error checking health of agent {agent_id}: {e}")
    
    async def _resolve_conflicts(self) -> None:
        """Resolve conflicts between agent decisions"""
        # This would implement conflict resolution logic
        # For example, if bed agent and staff agent have conflicting recommendations
        pass
    
    async def _update_system_metrics(self) -> None:
        """Update system-wide performance metrics"""
        # Calculate system-wide KPIs
        # Update monitoring dashboards
        pass
    
    async def process_external_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Process an external event and route to appropriate agents"""
        self.logger.info(f"Processing external event: {event.event_type}")
        
        # Determine which agents should handle this event
        target_agents = self._get_target_agents_for_event(event)
        
        results = {}
        
        # Send event to all relevant agents
        for agent_id in target_agents:
            agent = self.agents.get(agent_id)
            if agent:
                try:
                    result = await agent.process_event(event)
                    results[agent_id] = result
                except Exception as e:
                    self.logger.error(f"Agent {agent_id} failed to process event: {e}")
                    results[agent_id] = {"error": str(e)}
            else:
                self.logger.warning(f"Target agent not found: {agent_id}")
        
        return {
            "event_id": event.event_id,
            "processed_by": list(results.keys()),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_target_agents_for_event(self, event: AgentEvent) -> List[str]:
        """Determine which agents should handle a specific event"""
        event_type = event.event_type
        
        # Event routing logic
        routing_table = {
            "patient_admission_request": ["bed_management_agent", "staff_allocation_agent"],
            "patient_discharge": ["bed_management_agent", "supply_inventory_agent"],
            "equipment_maintenance_alert": ["equipment_tracker_agent"],
            "staff_shortage_alert": ["staff_allocation_agent", "bed_management_agent"],
            "supply_shortage_alert": ["supply_inventory_agent"],
            "emergency_admission": ["bed_management_agent", "staff_allocation_agent", "equipment_tracker_agent"],
        }
        
        return routing_table.get(event_type, [])
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()
        
        uptime = None
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "orchestrator_status": "running" if self.running else "stopped",
            "agent_count": len(self.agents),
            "agents": agent_statuses,
            "messages_processed": self.messages_processed,
            "coordination_events": self.coordination_events,
            "uptime_seconds": uptime,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        metrics = {
            "system_metrics": {
                "messages_per_second": self._calculate_message_rate(),
                "average_response_time": self._calculate_avg_response_time(),
                "error_rate": self._calculate_error_rate()
            },
            "agent_metrics": {}
        }
        
        # Collect metrics from all agents
        for agent_id, agent in self.agents.items():
            agent_status = agent.get_status()
            metrics["agent_metrics"][agent_id] = agent_status["metrics"]
        
        return metrics
    
    def _calculate_message_rate(self) -> float:
        """Calculate messages processed per second"""
        if not self.start_time:
            return 0.0
        
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        return self.messages_processed / elapsed if elapsed > 0 else 0.0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time across all agents"""
        # This would be implemented with proper timing measurements
        return 0.5  # Placeholder
    
    def _calculate_error_rate(self) -> float:
        """Calculate system error rate"""
        total_errors = sum(
            agent.metrics.errors_count 
            for agent in self.agents.values()
        )
        total_events = sum(
            agent.metrics.events_processed 
            for agent in self.agents.values()
        )
        
        return total_errors / total_events if total_events > 0 else 0.0
