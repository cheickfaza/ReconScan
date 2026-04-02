#!/usr/bin/env python3
"""
Email Scanner Module - Recherche d'informations à partir d'une adresse email
Intègre HaveIBeenPwned, Gravatar et d'autres services OSINT
"""

import hashlib
import json
import re
import time
import asyncio
from datetime import datetime
from pathlib import Path

import aiohttp
from colorama import init, Fore, Style

init(autoreset=True)


class EmailScanner:
    """Scanner d'emails pour recherche OSINT"""
    
    def __init__(self, email, timeout=10):
        self.email = email.lower().strip()
        self.timeout = timeout
        self.results = {
            "email": self.email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "breaches": [],
            "gravatar": {},
            "social_accounts": [],
            "domain_info": {},
            "errors": []
        }
        
    def validate_email(self):
        """Valide le format de l'email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, self.email):
            return True
        return False
    
    def hash_email_sha1(self):
        """Hash l'email en SHA1 pour HaveIBeenPwned"""
        return hashlib.sha1(self.email.encode('utf-8')).hexdigest().upper()
    
    def hash_email_md5(self):
        """Hash l'email en MD5 pour Gravatar"""
        return hashlib.md5(self.email.encode('utf-8')).hexdigest().lower()
    
    async def check_haveibeenpwned(self, session):
        """Vérifie les fuites de données via HaveIBeenPwned API"""
        print(f"\n{Fore.CYAN}🔍 Vérification HaveIBeenPwned...{Style.RESET_ALL}")
        
        try:
            # API non authentifiée (limitée)
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{self.email}"
            headers = {
                "user-agent": "ReconScan-OSINT-Tool",
                "hibp-api-key": ""  # Clé API optionnelle
            }
            
            async with session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status == 200:
                    breaches = await response.json()
                    self.results["breaches"] = [
                        {
                            "name": breach.get("Name", "Unknown"),
                            "domain": breach.get("Domain", "Unknown"),
                            "breach_date": breach.get("BreachDate", "Unknown"),
                            "added_date": breach.get("AddedDate", "Unknown"),
                            "description": breach.get("Description", ""),
                            "data_classes": breach.get("DataClasses", []),
                            "is_verified": breach.get("IsVerified", False),
                            "is_fabricated": breach.get("IsFabricated", False),
                            "is_sensitive": breach.get("IsSensitive", False),
                            "is_retired": breach.get("IsRetired", False),
                            "is_spam_list": breach.get("IsSpamList", False),
                            "logo_path": breach.get("LogoPath", ""),
                            "pwn_count": breach.get("PwnCount", 0)
                        }
                        for breach in breaches
                    ]
                    print(f"{Fore.RED}⚠️  {len(breaches)} fuite(s) de données trouvée(s)!{Style.RESET_ALL}")
                elif response.status == 404:
                    print(f"{Fore.GREEN}✓ Aucune fuite de données trouvée{Style.RESET_ALL}")
                elif response.status == 429:
                    print(f"{Fore.YELLOW}⚠️  Rate limit atteint pour HaveIBeenPwned{Style.RESET_ALL}")
                    self.results["errors"].append("HaveIBeenPwned: Rate limit")
                else:
                    print(f"{Fore.YELLOW}⚠️  Statut HTTP: {response.status}{Style.RESET_ALL}")
                    
        except asyncio.TimeoutError:
            print(f"{Fore.RED}✗ Délai dépassé pour HaveIBeenPwned{Style.RESET_ALL}")
            self.results["errors"].append("HaveIBeenPwned: Timeout")
        except Exception as e:
            print(f"{Fore.RED}✗ Erreur HaveIBeenPwned: {e}{Style.RESET_ALL}")
            self.results["errors"].append(f"HaveIBeenPwned: {str(e)}")
    
    async def check_gravatar(self, session):
        """Recherche le profil Gravatar associé à l'email"""
        print(f"\n{Fore.CYAN}🔍 Vérification Gravatar...{Style.RESET_ALL}")
        
        try:
            md5_hash = self.hash_email_md5()
            url = f"https://api.gravatar.com/3/md5/{md5_hash}"
            
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("entry"):
                        entry = data["entry"][0]
                        self.results["gravatar"] = {
                            "found": True,
                            "display_name": entry.get("displayName", ""),
                            "profile_url": entry.get("profileUrl", ""),
                            "thumbnail": entry.get("thumbnailUrl", ""),
                            "photos": entry.get("photos", []),
                            "urls": entry.get("urls", []),
                            "aboutme": entry.get("aboutme", ""),
                            "current_location": entry.get("currentLocation", ""),
                            "accounts": [
                                {
                                    "service": acc.get("shortname", ""),
                                    "username": acc.get("username", ""),
                                    "url": acc.get("url", "")
                                }
                                for acc in entry.get("accounts", [])
                            ]
                        }
                        print(f"{Fore.GREEN}✓ Profil Gravatar trouvé: {entry.get('displayName', 'N/A')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  Aucun profil Gravatar trouvé{Style.RESET_ALL}")
                        self.results["gravatar"] = {"found": False}
                else:
                    print(f"{Fore.YELLOW}⚠️  Statut HTTP: {response.status}{Style.RESET_ALL}")
                    self.results["gravatar"] = {"found": False}
                    
        except asyncio.TimeoutError:
            print(f"{Fore.RED}✗ Délai dépassé pour Gravatar{Style.RESET_ALL}")
            self.results["errors"].append("Gravatar: Timeout")
        except Exception as e:
            print(f"{Fore.RED}✗ Erreur Gravatar: {e}{Style.RESET_ALL}")
            self.results["errors"].append(f"Gravatar: {str(e)}")
    
    async def check_email_domains(self, session):
        """Recherche des informations sur le domaine de l'email"""
        print(f"\n{Fore.CYAN}🔍 Analyse du domaine...{Style.RESET_ALL}")
        
        try:
            domain = self.email.split('@')[1]
            
            # Vérification MX simple
            self.results["domain_info"] = {
                "domain": domain,
                "provider_type": self._guess_provider(domain)
            }
            
            print(f"{Fore.GREEN}✓ Domaine: {domain} ({self.results['domain_info']['provider_type']}){Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Erreur analyse domaine: {e}{Style.RESET_ALL}")
            self.results["errors"].append(f"Domain analysis: {str(e)}")
    
    def _guess_provider(self, domain):
        """Devine le type de fournisseur d'email"""
        known_providers = {
            "gmail.com": "Google Gmail",
            "googlemail.com": "Google Gmail",
            "outlook.com": "Microsoft Outlook",
            "hotmail.com": "Microsoft Hotmail",
            "live.com": "Microsoft Live",
            "yahoo.com": "Yahoo Mail",
            "yahoo.fr": "Yahoo Mail",
            "protonmail.com": "ProtonMail",
            "proton.me": "ProtonMail",
            "icloud.com": "Apple iCloud",
            "mail.com": "Mail.com",
            "aol.com": "AOL Mail",
            "yandex.com": "Yandex Mail",
            "gmx.com": "GMX",
            "zoho.com": "Zoho Mail"
        }
        
        return known_providers.get(domain, "Custom/Private Domain")
    
    async def check_social_from_gravatar(self, session):
        """Extrait les comptes sociaux depuis Gravatar"""
        if not self.results["gravatar"].get("found"):
            return
        
        print(f"\n{Fore.CYAN}🔍 Extraction comptes sociaux depuis Gravatar...{Style.RESET_ALL}")
        
        accounts = self.results["gravatar"].get("accounts", [])
        for account in accounts:
            if account.get("service") and account.get("username"):
                self.results["social_accounts"].append(account)
                print(f"  {Fore.GREEN}✓ {account['service']}: {account['username']}{Style.RESET_ALL}")
    
    async def run_scan(self):
        """Exécute tous les scans"""
        if not self.validate_email():
            print(f"{Fore.RED}✗ Email invalide: {self.email}{Style.RESET_ALL}")
            return False
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"SCAN EMAIL OSINT - {self.email}")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        async with aiohttp.ClientSession() as session:
            # Exécution parallèle des scans principaux
            await asyncio.gather(
                self.check_haveibeenpwned(session),
                self.check_gravatar(session),
                self.check_email_domains(session),
                return_exceptions=True
            )
            
            # Scan des comptes sociaux (dépend de Gravatar)
            await self.check_social_from_gravatar(session)
        
        return True
    
    def generate_report(self, output_format="json"):
        """Génère un rapport des résultats"""
        report_data = {
            "email": self.email,
            "timestamp": self.results["timestamp"],
            "summary": {
                "total_breaches": len(self.results["breaches"]),
                "gravatar_found": self.results["gravatar"].get("found", False),
                "social_accounts_found": len(self.results["social_accounts"]),
                "errors": len(self.results["errors"])
            },
            "results": self.results
        }
        
        if output_format == "json":
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        elif output_format == "text":
            return self._generate_text_report(report_data)
        else:
            return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_text_report(self, data):
        """Génère un rapport texte"""
        lines = []
        lines.append("=" * 60)
        lines.append("RAPPORT EMAIL OSINT - ReconScan")
        lines.append("=" * 60)
        lines.append(f"Email analysé: {data['email']}")
        lines.append(f"Date: {data['timestamp']}")
        lines.append("")
        
        # Résumé
        lines.append("RÉSUMÉ")
        lines.append("-" * 40)
        lines.append(f"Fuites de données: {data['summary']['total_breaches']}")
        lines.append(f"Profil Gravatar: {'Trouvé' if data['summary']['gravatar_found'] else 'Non trouvé'}")
        lines.append(f"Comptes sociaux: {data['summary']['social_accounts_found']}")
        lines.append(f"Erreurs: {data['summary']['errors']}")
        lines.append("")
        
        # Fuites de données
        if data['results']['breaches']:
            lines.append("FUITES DE DONNÉES TROUVÉES")
            lines.append("-" * 40)
            for breach in data['results']['breaches']:
                lines.append(f"• {breach['name']} ({breach['breach_date']})")
                lines.append(f"  Domaine: {breach['domain']}")
                lines.append(f"  Données compromises: {', '.join(breach['data_classes'])}")
                lines.append("")
        
        # Gravatar
        if data['results']['gravatar'].get('found'):
            lines.append("PROFIL GRAVATAR")
            lines.append("-" * 40)
            gravatar = data['results']['gravatar']
            lines.append(f"Nom: {gravatar.get('display_name', 'N/A')}")
            lines.append(f"URL: {gravatar.get('profile_url', 'N/A')}")
            if gravatar.get('aboutme'):
                lines.append(f"Bio: {gravatar['aboutme'][:100]}...")
            if gravatar.get('current_location'):
                lines.append(f"Localisation: {gravatar['current_location']}")
            lines.append("")
        
        # Comptes sociaux
        if data['results']['social_accounts']:
            lines.append("COMPTES SOCIAUX DÉCOUVERTS")
            lines.append("-" * 40)
            for account in data['results']['social_accounts']:
                lines.append(f"• {account['service']}: {account['username']}")
                if account.get('url'):
                    lines.append(f"  URL: {account['url']}")
            lines.append("")
        
        # Erreurs
        if data['results']['errors']:
            lines.append("ERREURS")
            lines.append("-" * 40)
            for error in data['results']['errors']:
                lines.append(f"⚠️  {error}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, filename=None, output_format="json"):
        """Sauvegarde le rapport dans un fichier"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            email_safe = self.email.replace('@', '_at_').replace('.', '_')
            filename = f"email_scan_{email_safe}_{timestamp}.{output_format}"
        
        report = self.generate_report(output_format)
        
        # Créer le dossier reports s'il n'existe pas
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        filepath = reports_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(filepath)


async def main():
    """Fonction principale pour test"""
    import sys
    
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Usage: python email_scanner.py <email>{Style.RESET_ALL}")
        sys.exit(1)
    
    email = sys.argv[1]
    scanner = EmailScanner(email)
    
    success = await scanner.run_scan()
    
    if success:
        # Sauvegarder le rapport
        filename = scanner.save_report()
        print(f"\n{Fore.GREEN}📄 Rapport sauvegardé: {filename}{Style.RESET_ALL}")
        
        # Afficher le rapport texte
        print("\n" + scanner.generate_report("text"))


if __name__ == "__main__":
    asyncio.run(main())