# shared/domain/models.py
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# --- ENUMS (Tipos y Estados) ---

class SourceType(str, Enum):
    TELEGRAM = "telegram"
    API = "api"
    SCHEDULER = "scheduler" # Para los CronJobs de Liferay/K8s

class ActionType(str, Enum):
    WEB_BROWSER = "web_browser" # Liferay / UIpip install pydantic
    API_CALL = "api_call"       # Middleware K8s
    SYS_QUERY = "sys_query"     # K8s nodes status
    KNOWLEDGE_QUERY = "rag_mcp" # JIRA / Documentación

class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# --- ENTIDADES BASE ---

class Intention(BaseModel):
    """Lo que el usuario o el sistema quiere lograr"""
    id: UUID = Field(default_factory=uuid4)
    source: SourceType
    user_id: str # Puede ser un chat_id de Telegram o "system"
    raw_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Action(BaseModel):
    """La tarea atómica que debe ejecutar un Agente/Executor"""
    id: UUID = Field(default_factory=uuid4)
    intention_id: UUID
    action_type: ActionType
    payload: Dict[str, Any] # Ej: {"url": "liferay.com", "check": "login_form"}
    status: Status = Status.PENDING
    retry_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BillingMetadata(BaseModel):
    """Trazabilidad FinOps para el Dashboard"""
    tokens_in: int = 0
    tokens_out: int = 0
    model_name: str = "unknown"
    provider: str = "unknown"
    estimated_cost_usd: float = 0.0

class Outcome(BaseModel):
    """El resultado devuelto por el Executor tras hacer la Acción"""
    action_id: UUID
    intention_id: UUID
    success: bool
    result_data: Dict[str, Any] # Ej: {"latency_ms": 120, "status_code": 200}
    error_message: Optional[str] = None
    billing: BillingMetadata = Field(default_factory=BillingMetadata)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))