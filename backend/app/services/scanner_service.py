"""
Scanner service - Orchestre les différents scanners
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.scan import ScanHistory, ScanResult
from app.schemas.scan import ScanType, ScanStatus


class ScannerService:
    """Service pour gérer les scans"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_scan(
        self,
        scan_type: ScanType,
        query: str,
        timeout: int = 10,
        concurrent: int = 10
    ) -> ScanHistory:
        """Crée une nouvelle entrée de scan"""
        scan = ScanHistory(
            scan_type=scan_type.value,
            query=query,
            status=ScanStatus.PENDING.value,
            created_at=datetime.utcnow()
        )
        self.db.add(scan)
        await self.db.commit()
        await self.db.refresh(scan)
        return scan
    
    async def update_scan_status(
        self,
        scan_id: int,
        status: ScanStatus,
        summary: Optional[Dict[str, Any]] = None
    ):
        """Met à jour le statut d'un scan"""
        scan = await self.db.get(ScanHistory, scan_id)
        if scan:
            scan.status = status.value
            if status == ScanStatus.COMPLETED:
                scan.completed_at = datetime.utcnow()
            if summary:
                scan.total_platforms = summary.get("total", 0)
                scan.found_count = summary.get("found", 0)
                scan.not_found_count = summary.get("not_found", 0)
                scan.error_count = summary.get("errors", 0)
            await self.db.commit()
    
    async def add_result(
        self,
        scan_id: int,
        platform: str,
        url: Optional[str],
        status: str,
        response_time: Optional[float] = None,
        http_status: Optional[int] = None,
        data: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Ajoute un résultat au scan"""
        result = ScanResult(
            scan_id=scan_id,
            platform=platform,
            url=url,
            status=status,
            response_time=response_time,
            http_status=http_status,
            data=data,
            error_message=error_message
        )
        self.db.add(result)
        await self.db.commit()
    
    async def get_scan(self, scan_id: int) -> Optional[ScanHistory]:
        """Récupère un scan par son ID"""
        return await self.db.get(ScanHistory, scan_id)
    
    async def get_scan_history(
        self,
        limit: int = 50,
        scan_type: Optional[str] = None
    ) -> List[ScanHistory]:
        """Récupère l'historique des scans"""
        query = select(ScanHistory)
        if scan_type:
            query = query.where(ScanHistory.scan_type == scan_type)
        query = query.order_by(ScanHistory.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def run_username_scan(
        self,
        scan_id: int,
        username: str,
        timeout: int = 10,
        concurrent: int = 10,
        deep_scan: bool = False
    ):
        """Exécute un scan de pseudo"""
        from scanners.username_scanner import UsernameScanner
        
        await self.update_scan_status(scan_id, ScanStatus.RUNNING)
        
        scanner = UsernameScanner(username, timeout, concurrent)
        
        try:
            # Exécuter le scan
            results = await scanner.run_search()
            
            # Sauvegarder les résultats
            for result in results:
                await self.add_result(
                    scan_id=scan_id,
                    platform=result.get("platform", "Unknown"),
                    url=result.get("url"),
                    status=result.get("status", "unknown"),
                    response_time=result.get("response_time"),
                    http_status=result.get("http_status"),
                    data=result,
                    error_message=result.get("error")
                )
            
            # Si deep scan activé, analyser les URLs trouvées
            if deep_scan:
                found_urls = [r.get("url") for r in results if r.get("status") == "found" and r.get("url")]
                if found_urls:
                    await self._run_deep_scan_on_urls(scan_id, found_urls, timeout)
            
            # Mettre à jour le statut
            summary = {
                "total": len(results),
                "found": len([r for r in results if r.get("status") == "found"]),
                "not_found": len([r for r in results if r.get("status") == "not_found"]),
                "errors": len([r for r in results if r.get("status") not in ["found", "not_found"]])
            }
            await self.update_scan_status(scan_id, ScanStatus.COMPLETED, summary)
            
        except Exception as e:
            await self.update_scan_status(scan_id, ScanStatus.FAILED)
            await self.add_result(
                scan_id=scan_id,
                platform="system",
                url=None,
                status="error",
                error_message=str(e)
            )
    
    async def run_email_scan(
        self,
        scan_id: int,
        email: str,
        timeout: int = 10
    ):
        """Exécute un scan d'email"""
        from scanners.email_scanner import EmailScanner
        
        await self.update_scan_status(scan_id, ScanStatus.RUNNING)
        
        scanner = EmailScanner(email, timeout)
        
        try:
            success = await scanner.run_scan()
            
            if success:
                # Sauvegarder les résultats
                results = scanner.results
                
                # Sauvegarder les fuites
                for breach in results.get("breaches", []):
                    await self.add_result(
                        scan_id=scan_id,
                        platform="HaveIBeenPwned",
                        url=None,
                        status="found",
                        data=breach
                    )
                
                # Sauvegarder Gravatar
                if results.get("gravatar", {}).get("found"):
                    await self.add_result(
                        scan_id=scan_id,
                        platform="Gravatar",
                        url=results["gravatar"].get("profile_url"),
                        status="found",
                        data=results["gravatar"]
                    )
                
                # Sauvegarder les comptes sociaux
                for account in results.get("social_accounts", []):
                    await self.add_result(
                        scan_id=scan_id,
                        platform=account.get("service", "Unknown"),
                        url=account.get("url"),
                        status="found",
                        data=account
                    )
                
                summary = {
                    "total": 1,
                    "found": len(results.get("breaches", [])) + (1 if results.get("gravatar", {}).get("found") else 0),
                    "not_found": 0,
                    "errors": len(results.get("errors", []))
                }
                await self.update_scan_status(scan_id, ScanStatus.COMPLETED, summary)
            
        except Exception as e:
            await self.update_scan_status(scan_id, ScanStatus.FAILED)
            await self.add_result(
                scan_id=scan_id,
                platform="system",
                url=None,
                status="error",
                error_message=str(e)
            )
    
    async def _run_deep_scan_on_urls(self, scan_id: int, urls: List[str], timeout: int):
        """Exécute un deep scan sur des URLs"""
        from scanners.deep_scanner import DeepScanner
        
        scanner = DeepScanner(urls, timeout)
        results = await scanner.run_scan()
        
        for result in results:
            tech_names = [t.get("name") for t in result.get("technologies", [])]
            await self.add_result(
                scan_id=scan_id,
                platform=f"Deep: {result.get('url', 'Unknown')[:50]}",
                url=result.get("url"),
                status=result.get("status", "unknown"),
                data={
                    "profile": result.get("profile_data", {}),
                    "technologies": tech_names,
                    "files": result.get("files_found", [])
                }
            )