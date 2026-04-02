"""
Scan API routes
"""

import asyncio
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.schemas.scan import (
    ScanRequest,
    ScanResponse,
    ScanHistoryResponse,
    ScanResultResponse,
    ScanType,
    ScanStatus
)
from app.services.scanner_service import ScannerService

router = APIRouter(prefix="/scan", tags=["Scans"])


@router.post("/", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Crée et lance un nouveau scan"""
    service = ScannerService(db)
    
    # Créer l'entrée de scan
    scan = await service.create_scan(
        scan_type=request.scan_type,
        query=request.query,
        timeout=request.timeout,
        concurrent=request.concurrent
    )
    
    # Lancer le scan en arrière-plan
    if request.scan_type == ScanType.USERNAME:
        background_tasks.add_task(
            service.run_username_scan,
            scan.id,
            request.query,
            request.timeout,
            request.concurrent,
            request.deep_scan
        )
    elif request.scan_type == ScanType.EMAIL:
        background_tasks.add_task(
            service.run_email_scan,
            scan.id,
            request.query,
            request.timeout
        )
    
    return ScanResponse(
        scan_id=scan.id,
        scan_type=scan.scan_type,
        query=scan.query,
        status=scan.status,
        message="Scan lancé avec succès",
        summary={"total": 0, "found": 0, "not_found": 0, "errors": 0},
        results=[]
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Récupère les détails d'un scan"""
    service = ScannerService(db)
    scan = await service.get_scan(scan_id)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    results = [
        ScanResultResponse(
            id=r.id,
            platform=r.platform,
            url=r.url,
            status=r.status,
            response_time=r.response_time,
            http_status=r.http_status,
            data=r.data,
            error_message=r.error_message
        )
        for r in scan.results
    ]
    
    return ScanResponse(
        scan_id=scan.id,
        scan_type=scan.scan_type,
        query=scan.query,
        status=scan.status,
        message="Scan récupéré avec succès",
        summary={
            "total": scan.total_platforms,
            "found": scan.found_count,
            "not_found": scan.not_found_count,
            "errors": scan.error_count
        },
        results=results
    )


@router.get("/history", response_model=List[ScanHistoryResponse])
async def get_scan_history(
    limit: int = Query(50, ge=1, le=100),
    scan_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Récupère l'historique des scans"""
    service = ScannerService(db)
    scans = await service.get_scan_history(limit=limit, scan_type=scan_type)
    
    return [
        ScanHistoryResponse(
            id=s.id,
            scan_type=s.scan_type,
            query=s.query,
            created_at=s.created_at,
            completed_at=s.completed_at,
            status=s.status,
            total_platforms=s.total_platforms,
            found_count=s.found_count,
            not_found_count=s.not_found_count,
            error_count=s.error_count,
            results=[
                ScanResultResponse(
                    id=r.id,
                    platform=r.platform,
                    url=r.url,
                    status=r.status,
                    response_time=r.response_time,
                    http_status=r.http_status,
                    data=r.data,
                    error_message=r.error_message
                )
                for r in s.results
            ]
        )
        for s in scans
    ]


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Supprime un scan"""
    from sqlalchemy import delete
    from app.models.scan import ScanHistory
    
    scan = await db.get(ScanHistory, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    await db.delete(scan)
    await db.commit()
    
    return {"message": "Scan supprimé avec succès"}