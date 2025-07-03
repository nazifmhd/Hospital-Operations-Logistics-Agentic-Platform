"""
Base agent class for the Hospital Operations Platform
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentEvent(BaseModel):
    """Agent event model"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class AgentMessage(BaseModel):
    """Agent message model"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_agent: str
    receiver_agent: Optional[str] = None  # None for broadcast
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class AgentMetrics(BaseModel):
    """Agent performance metrics"""
    events_processed: int = 0
    decisions_made: int = 0
    errors_count: int = 0
    average_response_time: float = 0.0
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """Base class for all hospital operation agents"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.description = description
        self.config = config or {}
        self.status = AgentStatus.INITIALIZING
        self.metrics = AgentMetrics()
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Event handlers
        self._event_handlers: Dict[str, List[callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
        self.logger.info(f"Agent {agent_id} initialized")
    
    async def initialize(self) -> None:
        """Initialize the agent"""
        try:
            self.logger.info(f"Initializing agent {self.agent_id}")
            await self._initialize_agent()
            self.status = AgentStatus.RUNNING
            self._running = True
            self.logger.info(f"Agent {self.agent_id} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            raise
    
    async def start(self) -> None:
        """Start the agent processing loop"""
        if not self._running:
            await self.initialize()
        
        self.logger.info(f"Starting agent {self.agent_id}")
        
        # Start the main processing loop
        await asyncio.gather(
            self._process_messages(),
            self._agent_main_loop(),
            return_exceptions=True
        )
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info(f"Stopping agent {self.agent_id}")
        self._running = False
        self.status = AgentStatus.SHUTDOWN
        await self._cleanup_agent()
    
    async def send_message(self, message: AgentMessage) -> None:
        """Send a message to another agent or broadcast"""
        self.logger.debug(f"Sending message: {message.message_type} to {message.receiver_agent}")
        # This will be implemented by the orchestrator
        pass
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent"""
        await self._message_queue.put(message)
    
    async def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process an external event"""
        try:
            self.logger.debug(f"Processing event: {event.event_type}")
            self.metrics.events_processed += 1
            self.metrics.last_activity = datetime.utcnow()
            
            result = await self._process_event(event)
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_type}: {e}")
            self.metrics.errors_count += 1
            raise
    
    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "metrics": self.metrics.dict(),
            "description": self.description
        }
    
    async def _process_messages(self) -> None:
        """Process incoming messages"""
        while self._running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=1.0
                )
                
                self.logger.debug(f"Processing message: {message.message_type}")
                await self._handle_message(message)
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                self.metrics.errors_count += 1
    
    async def _agent_main_loop(self) -> None:
        """Main agent processing loop - to be implemented by subclasses"""
        while self._running:
            try:
                await self._agent_tick()
                await asyncio.sleep(self.config.get("tick_interval", 1.0))
            except Exception as e:
                self.logger.error(f"Error in agent main loop: {e}")
                self.metrics.errors_count += 1
                await asyncio.sleep(5.0)  # Backoff on error
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    async def _initialize_agent(self) -> None:
        """Initialize agent-specific resources"""
        pass
    
    @abstractmethod
    async def _cleanup_agent(self) -> None:
        """Cleanup agent-specific resources"""
        pass
    
    @abstractmethod
    async def _process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process an event specific to this agent"""
        pass
    
    @abstractmethod
    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle a message from another agent"""
        pass
    
    @abstractmethod
    async def _agent_tick(self) -> None:
        """Perform one iteration of agent processing"""
        pass
    
    @abstractmethod
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on the given context"""
        pass
