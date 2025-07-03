"""
Agent management endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class EventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]
    correlation_id: str = None


@router.get("/")
async def get_all_agents(request: Request) -> Dict[str, Any]:
    """Get status of all agents"""
    try:
        orchestrator = request.app.state.orchestrator
        system_status = orchestrator.get_system_status()
        return system_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@router.get("/{agent_id}")
async def get_agent_status(agent_id: str, request: Request) -> Dict[str, Any]:
    """Get status of a specific agent"""
    try:
        orchestrator = request.app.state.orchestrator
        agent = orchestrator.agents.get(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return agent.get_status()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@router.post("/events")
async def process_event(event: EventRequest, request: Request) -> Dict[str, Any]:
    """Process an external event through the agent system"""
    try:
        from core.base_agent import AgentEvent
        
        # Create agent event
        agent_event = AgentEvent(
            agent_id="external",
            event_type=event.event_type,
            data=event.data,
            correlation_id=event.correlation_id
        )
        
        # Process through orchestrator
        orchestrator = request.app.state.orchestrator
        result = await orchestrator.process_external_event(agent_event)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process event: {str(e)}")


@router.get("/metrics/performance")
async def get_performance_metrics(request: Request) -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        orchestrator = request.app.state.orchestrator
        metrics = await orchestrator.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.post("/{agent_id}/restart")
async def restart_agent(agent_id: str, request: Request) -> Dict[str, Any]:
    """Restart a specific agent"""
    try:
        orchestrator = request.app.state.orchestrator
        agent = orchestrator.agents.get(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Stop and restart agent
        await agent.stop()
        await agent.start()
        
        return {"message": f"Agent {agent_id} restarted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart agent: {str(e)}")
