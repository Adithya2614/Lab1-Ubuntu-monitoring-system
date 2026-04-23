"""
Metrics Schemas
================
Pydantic v2 request/response models for metrics data.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class MetricDataPoint(BaseModel):
    """A single metrics data point."""
    cpu_load: float
    ram_used: int
    ram_total: int
    ram_percentage: float
    disk_percentage: float
    network_rx: Optional[int] = None
    network_tx: Optional[int] = None
    timestamp: datetime


class MetricsHistoryResponse(BaseModel):
    """Response for metrics history of a PC."""
    pc_id: int
    pc_hostname: str
    data_points: list[MetricDataPoint]
    latest: Optional[MetricDataPoint] = None


class MetricsReceiveRequest(BaseModel):
    """
    Request body for receiving metrics (backward-compatible with MetricData).
    """
    node_id: str
    metrics: dict
