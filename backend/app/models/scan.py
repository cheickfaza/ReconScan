"""
Scan result models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class ScanHistory(Base):
    """Historique des recherches"""
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String(50), nullable=False)  # username, email, deep_scan, correlation
    query = Column(String(255), nullable=False)  # pseudo, email, or URL
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    total_platforms = Column(Integer, default=0)
    found_count = Column(Integer, default=0)
    not_found_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Relations
    results = relationship("ScanResult", back_populates="scan", cascade="all, delete-orphan")


class ScanResult(Base):
    """Résultats individuels des scans"""
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_history.id"), nullable=False)
    platform = Column(String(100), nullable=False)
    url = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # found, not_found, error, timeout, etc.
    response_time = Column(Float, nullable=True)
    http_status = Column(Integer, nullable=True)
    data = Column(JSON, nullable=True)  # Données supplémentaires (profil, etc.)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation
    scan = relationship("ScanHistory", back_populates="results")