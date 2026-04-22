from pydantic import BaseModel
from typing import List, Optional, Any

class ActionRequest(BaseModel):
    target: str
    action_type: str  # e.g., 'ping', 'collect_metrics', 'install_package'
    parameters: Optional[dict] = {}

class MetricData(BaseModel):
    node_id: str
    metrics: dict

class Node(BaseModel):
    id: str
    name: str
    status: str
    ip: Optional[str] = None

class AddNodeRequest(BaseModel):
    hostname: str
    user: str
    password: str
    ip: Optional[str] = None
