"""
Core module for Hospital Operations Platform
"""

from .config import settings
from .base_agent import BaseAgent, AgentEvent, AgentMessage

__all__ = [
    "settings",
    "BaseAgent", 
    "AgentEvent",
    "AgentMessage"
]
