"""
Base Agent class for olKAN v2.0
Foundation for all AI agents in the system
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentPriority(Enum):
    """Agent execution priority"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str
    agent_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: AgentPriority = AgentPriority.NORMAL
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class AgentResult:
    """Result from agent execution"""
    task_id: str
    agent_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Abstract base class for all AI agents"""
    
    def __init__(
        self, 
        agent_id: str, 
        name: str, 
        description: str = "",
        max_concurrent_tasks: int = 5
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.max_concurrent_tasks = max_concurrent_tasks
        self.status = AgentStatus.IDLE
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: List[AgentTask] = []
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self._task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._shutdown_event = asyncio.Event()
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a specific task - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def validate_task_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate task parameters - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_supported_task_types(self) -> List[str]:
        """Get list of supported task types - must be implemented by subclasses"""
        pass
    
    async def submit_task(
        self, 
        task_type: str, 
        parameters: Dict[str, Any],
        priority: AgentPriority = AgentPriority.NORMAL
    ) -> str:
        """Submit a new task to the agent"""
        task_id = f"{self.agent_id}_{task_type}_{datetime.utcnow().timestamp()}"
        
        # Validate parameters
        if not self.validate_task_parameters(parameters):
            raise ValueError(f"Invalid parameters for task type: {task_type}")
        
        if task_type not in self.get_supported_task_types():
            raise ValueError(f"Unsupported task type: {task_type}")
        
        # Create task
        task = AgentTask(
            id=task_id,
            agent_id=self.agent_id,
            task_type=task_type,
            parameters=parameters,
            priority=priority
        )
        
        # Add to active tasks
        self.active_tasks[task_id] = task
        
        # Execute task asynchronously
        asyncio.create_task(self._execute_task_async(task))
        
        self.logger.info(f"Task {task_id} submitted successfully")
        return task_id
    
    async def _execute_task_async(self, task: AgentTask):
        """Execute task asynchronously with proper resource management"""
        async with self._task_semaphore:
            try:
                task.status = AgentStatus.RUNNING
                task.started_at = datetime.utcnow()
                
                self.logger.info(f"Starting task {task.id}")
                
                # Execute the task
                result = await self.execute_task(task)
                
                # Update task with result
                task.status = AgentStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result.data
                
                if result.execution_time:
                    task.metadata = task.metadata or {}
                    task.metadata["execution_time"] = result.execution_time
                
                # Move to completed tasks
                self.completed_tasks.append(task)
                del self.active_tasks[task.id]
                
                self.logger.info(f"Task {task.id} completed successfully")
                
            except Exception as e:
                # Handle task failure
                task.status = AgentStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                
                # Move to completed tasks
                self.completed_tasks.append(task)
                if task.id in self.active_tasks:
                    del self.active_tasks[task.id]
                
                self.logger.error(f"Task {task.id} failed: {str(e)}")
    
    async def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get the status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return task
        
        return None
    
    async def get_task_result(self, task_id: str) -> Optional[AgentResult]:
        """Get the result of a completed task"""
        task = await self.get_task_status(task_id)
        if task and task.status == AgentStatus.COMPLETED:
            return AgentResult(
                task_id=task.id,
                agent_id=task.agent_id,
                success=True,
                data=task.result,
                execution_time=task.metadata.get("execution_time") if task.metadata else None
            )
        elif task and task.status == AgentStatus.FAILED:
            return AgentResult(
                task_id=task.id,
                agent_id=task.agent_id,
                success=False,
                error=task.error
            )
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status == AgentStatus.RUNNING:
                task.status = AgentStatus.FAILED
                task.error = "Task cancelled by user"
                task.completed_at = datetime.utcnow()
                
                # Move to completed tasks
                self.completed_tasks.append(task)
                del self.active_tasks[task_id]
                
                self.logger.info(f"Task {task_id} cancelled")
                return True
        
        return False
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "supported_task_types": self.get_supported_task_types(),
            "statistics": {
                "total_tasks_processed": len(self.completed_tasks),
                "successful_tasks": len([t for t in self.completed_tasks if t.status == AgentStatus.COMPLETED]),
                "failed_tasks": len([t for t in self.completed_tasks if t.status == AgentStatus.FAILED])
            }
        }
    
    async def get_recent_tasks(self, limit: int = 10) -> List[AgentTask]:
        """Get recent completed tasks"""
        return sorted(
            self.completed_tasks, 
            key=lambda t: t.completed_at or t.created_at, 
            reverse=True
        )[:limit]
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        # Remove old completed tasks
        self.completed_tasks = [
            task for task in self.completed_tasks
            if (task.completed_at or task.created_at).timestamp() > cutoff_time
        ]
        
        self.logger.info(f"Cleaned up old tasks older than {max_age_hours} hours")
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        self.logger.info(f"Shutting down agent {self.agent_id}")
        
        # Set shutdown event
        self._shutdown_event.set()
        
        # Wait for active tasks to complete (with timeout)
        if self.active_tasks:
            self.logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete")
            
            # Wait up to 30 seconds for tasks to complete
            for _ in range(30):
                if not self.active_tasks:
                    break
                await asyncio.sleep(1)
            
            # Cancel remaining tasks
            for task_id in list(self.active_tasks.keys()):
                await self.cancel_task(task_id)
        
        self.status = AgentStatus.IDLE
        self.logger.info(f"Agent {self.agent_id} shutdown complete")
    
    def is_shutdown(self) -> bool:
        """Check if agent is shutdown"""
        return self._shutdown_event.is_set()
    
    async def wait_for_shutdown(self):
        """Wait for shutdown event"""
        await self._shutdown_event.wait()


class AgentManager:
    """Manages multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent_manager")
    
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent {agent.agent_id} is already registered")
        
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [agent.get_agent_status() for agent in self.agents.values()]
    
    async def submit_task_to_agent(
        self, 
        agent_id: str, 
        task_type: str, 
        parameters: Dict[str, Any],
        priority: AgentPriority = AgentPriority.NORMAL
    ) -> str:
        """Submit a task to a specific agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        return await agent.submit_task(task_type, parameters, priority)
    
    async def shutdown_all_agents(self):
        """Shutdown all registered agents"""
        self.logger.info("Shutting down all agents")
        
        shutdown_tasks = [
            agent.shutdown() for agent in self.agents.values()
        ]
        
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.logger.info("All agents shutdown complete")


# Global agent manager instance
agent_manager = AgentManager()
