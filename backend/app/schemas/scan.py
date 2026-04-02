"""
Scan schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Types de scan"""
    USERNAME = "username"
    EMAIL = "email"
    DEEP_SCAN = "deep_scan"
    CORRELATION = "correlation"


class ScanStatus(str, Enum):
    """Statuts de scan"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanRequest(BaseModel):
    """Requête de scan"""
    scan_type: ScanType = Field(..., description="Type de scan")
    query: str = Field(..., min_length=2, description="Pseudo, email ou URL à analyser")
    timeout: Optional[int] = Field(10, ge=1, le=60, description="Timeout en secondes")
    concurrent: Optional[int] = Field(10, ge=1, le=50, description="Requêtes concurrentes")
    deep_scan: Optional[bool] = Field(False, description="Activer le deep scan")


class ScanResultResponse(BaseModel):
    """Résultat individuel"""
    id: int
    platform: str
    url: Optional[str]
    status: str
    response_time: Optional[float]
    http_status: Optional[int]
    data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    """Historique de scan"""
    id: int
    scan_type: str
    query: str
    created_at: datetime
    completed_at: Optional[datetime]
    status: str
    total_platforms: int
    found_count: int
    not_found_count: int
    error_count: int
    results: Optional[List[ScanResultResponse]] = []
    
    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    """Réponse de scan"""
    scan_id: int
    scan_type: str
    query: str
    status: str
    message: str
    summary: Optional[Dict[str, Any]] = None
    results: Optional[List[ScanResultResponse]] = []