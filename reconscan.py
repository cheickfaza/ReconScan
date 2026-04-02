#!/usr/bin/env python3
"""
ReconScan - Outil OSINT de recherche de pseudo
Permet de trouver la présence d'un utilisateur sur différentes plateformes
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import aiohttp
from colorama import init, Fore, Style

# Initialiser colorama
init(autoreset=True)

# Liste des plateformes à vérifier
PLATFORMS = {
    # Réseaux sociaux
    "GitHub": {
        "url": "https://api.github.com/users/{}",
        "type": "api",
        "method": "GET",
        "status_code": 200
    },
    "Twitter/X": {
        "url": "https://nitter.net/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Reddit": {
        "url": "https://www.reddit.com/user/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Instagram": {
        "url": "https://www.instagram.com/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Facebook": {
        "url": "https://www.facebook.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "TikTok": {
        "url": "https://www.tiktok.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "LinkedIn": {
        "url": "https://www.linkedin.com/in/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Plateformes de développement
    "GitLab": {
        "url": "https://gitlab.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Stack Overflow": {
        "url": "https://stackoverflow.com/users/tagged/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Dev.to": {
        "url": "https://dev.to/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "CodePen": {
        "url": "https://codepen.io/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "npm": {
        "url": "https://www.npmjs.com/~{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "PyPI": {
        "url": "https://pypi.org/user/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Plateformes de hacking et cybersécurité
    "HackTheBox": {
        "url": "https://www.hackthebox.com/profile/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "TryHackMe": {
        "url": "https://tryhackme.com/p/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Bugcrowd": {
        "url": "https://bugcrowd.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "HackerOne": {
        "url": "https://hackerone.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "PentesterLab": {
        "url": "https://pentesterlab.com/profile/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Root-Me": {
        "url": "https://www.root-me.org/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "CTFtime": {
        "url": "https://ctftime.org/user/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "OverTheWire": {
        "url": "https://overthewire.org/wargames/",
        "type": "special",
        "note": "Recherche manuelle requise"
    },
    "HackThisSite": {
        "url": "https://www.hackthissite.org/user/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "WeChall": {
        "url": "https://www.wechall.net/profile/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "SecurityScorecard": {
        "url": "https://securityscorecard.com/profile/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "VulnCon": {
        "url": "https://vulncon.com/user/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Plateformes de développement avancé
    "Bitbucket": {
        "url": "https://bitbucket.org/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "SourceForge": {
        "url": "https://sourceforge.net/u/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Docker Hub": {
        "url": "https://hub.docker.com/u/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Ansible Galaxy": {
        "url": "https://galaxy.ansible.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "RubyGems": {
        "url": "https://rubygems.org/profiles/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Packagist": {
        "url": "https://packagist.org/packages/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Maven": {
        "url": "https://mvnrepository.com/artifact/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "NuGet": {
        "url": "https://www.nuget.org/profiles/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Crates.io": {
        "url": "https://crates.io/users/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Go Packages": {
        "url": "https://pkg.go.dev/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Forums techniques et hacking
    "0x00sec": {
        "url": "https://0x00sec.org/u/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "KernelMode": {
        "url": "https://www.kernelmode.info/forum/memberlist.php?mode=viewprofile&u={}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Reverse Engineering Stack Exchange": {
        "url": "https://reverseengineering.stackexchange.com/users/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Information Security Stack Exchange": {
        "url": "https://security.stackexchange.com/users/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "XDA Developers": {
        "url": "https://forum.xda-developers.com/m/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Guided Hacking": {
        "url": "https://guidedhacking.com/members/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "UnknownCheats": {
        "url": "https://www.unknowncheats.me/forum/members/{}.html",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Elitepvpers": {
        "url": "https://www.elitepvpers.com/forum/members/{}.html",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Hack Forums": {
        "url": "https://www.hackforums.net/member.php?action=profile&uid={}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Cracked.to": {
        "url": "https://cracked.to/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Nulled": {
        "url": "https://www.nulled.to/member/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "BlackHatWorld": {
        "url": "https://www.blackhatworld.com/members/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Warrior Forum": {
        "url": "https://www.warriorforum.com/members/{}.html",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Plateformes de blogging technique
    "Hashnode": {
        "url": "https://{}.hashnode.dev/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Substack": {
        "url": "https://substack.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Ghost": {
        "url": "https://{}.ghost.io/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Réseaux sociaux professionnels
    "AngelList": {
        "url": "https://angel.co/u/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "ProductHunt": {
        "url": "https://www.producthunt.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Indie Hackers": {
        "url": "https://www.indiehackers.com/user/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Plateformes de données et recherche
    "Kaggle": {
        "url": "https://www.kaggle.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Google Scholar": {
        "url": "https://scholar.google.com/citations?user={}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "ResearchGate": {
        "url": "https://www.researchgate.net/profile/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Academia.edu": {
        "url": "https://independent.academia.edu/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "arXiv": {
        "url": "https://arxiv.org/search/?searchtype=author&query={}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Plateformes de veille et curation
    "Pinboard": {
        "url": "https://pinboard.in/u:{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Pocket": {
        "url": "https://getpocket.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Flipboard": {
        "url": "https://flipboard.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Mastodon": {
        "url": "https://mastodon.social/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Forums et communautés
    "4chan": {
        "url": "https://boards.4channel.org/search/post?q={}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Quora": {
        "url": "https://www.quora.com/profile/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Medium": {
        "url": "https://medium.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Tumblr": {
        "url": "https://{}.tumblr.com/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "VK": {
        "url": "https://vk.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    
    # Jeux vidéo
    "Steam": {
        "url": "https://steamcommunity.com/id/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Twitch": {
        "url": "https://api.twitch.tv/helix/users?login={}",
        "type": "api",
        "method": "GET",
        "status_code": 200
    },
    "Xbox": {
        "url": "https://xboxgamertag.com/search/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "PlayStation": {
        "url": "https://psnprofiles.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Discord": {
        "url": "https://discord.com",
        "type": "special",
        "note": "Recherche manuelle requise"
    },
    
    # Services de messagerie
    "Gmail": {
        "url": "https://mail.google.com",
        "type": "special",
        "note": "Vérification manuelle requise"
    },
    "ProtonMail": {
        "url": "https://protonmail.com",
        "type": "special",
        "note": "Vérification manuelle requise"
    },
    
    # Autres plateformes
    "Pinterest": {
        "url": "https://www.pinterest.com/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "SoundCloud": {
        "url": "https://soundcloud.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Spotify": {
        "url": "https://open.spotify.com/user/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "YouTube": {
        "url": "https://www.youtube.com/@{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Vimeo": {
        "url": "https://vimeo.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Flickr": {
        "url": "https://www.flickr.com/people/{}/",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "500px": {
        "url": "https://500px.com/p/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Behance": {
        "url": "https://www.behance.net/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Dribbble": {
        "url": "https://dribbble.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "About.me": {
        "url": "https://about.me/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Linktree": {
        "url": "https://linktr.ee/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Patreon": {
        "url": "https://www.patreon.com/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Cash App": {
        "url": "https://cash.app/${}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Venmo": {
        "url": "https://account.venmo.com/u/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Keybase": {
        "url": "https://keybase.io/{}",
        "type": "api",
        "method": "GET",
        "status_code": 200
    },
    "Telegram": {
        "url": "https://t.me/{}",
        "type": "web",
        "method": "GET",
        "status_code": 200
    },
    "Signal": {
        "url": "https://signal.org",
        "type": "special",
        "note": "Vérification manuelle requise"
    },
    "WhatsApp": {
        "url": "https://wa.me/",
        "type": "special",
        "note": "Vérification manuelle requise"
    },
    "Skype": {
        "url": "https://join.skype.com",
        "type": "special",
        "note": "Vérification manuelle requise"
    },
}


class ReconScan:
    def __init__(self, username, timeout=10, max_concurrent=10):
        self.username = username
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.results = []
        self.found = []
        self.not_found = []
        self.errors = []
        
    async def check_platform(self, session, platform_name, platform_info):
        """Vérifie la présence d'un pseudo sur une plateforme"""
        url = platform_info["url"].format(self.username)
        result = {
            "platform": platform_name,
            "url": url,
            "status": "unknown",
            "response_time": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            if platform_info.get("type") == "special":
                result["status"] = "manual"
                result["note"] = platform_info.get("note", "Vérification manuelle requise")
                result["response_time"] = 0
                return result
            
            async with session.get(url, allow_redirects=True, timeout=self.timeout) as response:
                elapsed = time.time() - start_time
                result["response_time"] = round(elapsed, 3)
                result["http_status"] = response.status
                
                # Logique de détection basée sur le code de statut
                expected_status = platform_info.get("status_code", 200)
                
                if response.status == expected_status:
                    result["status"] = "found"
                elif response.status == 404:
                    result["status"] = "not_found"
                elif response.status == 403:
                    result["status"] = "restricted"
                elif response.status == 429:
                    result["status"] = "rate_limited"
                else:
                    result["status"] = "unknown"
                    result["error"] = f"Code HTTP: {response.status}"
                    
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error"] = "Délai d'attente dépassé"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result
    
    async def run_search(self):
        """Exécute la recherche sur toutes les plateformes"""
        print(f"\n{Fore.CYAN}🔍 Recherche du pseudo: {Style.BRIGHT}{self.username}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏱️  Plateformes vérifiées: {len(PLATFORMS)}{Style.RESET_ALL}\n")
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for platform_name, platform_info in PLATFORMS.items():
                task = self.check_platform_with_semaphore(session, platform_name, platform_info, semaphore)
                tasks.append(task)
            
            # Exécuter toutes les tâches et collecter les résultats
            self.results = await asyncio.gather(*tasks)
            
        # Trier les résultats
        for result in self.results:
            if result["status"] in ["found"]:
                self.found.append(result)
            elif result["status"] in ["not_found"]:
                self.not_found.append(result)
            else:
                self.errors.append(result)
                
    async def check_platform_with_semaphore(self, session, platform_name, platform_info, semaphore):
        """Vérifie une plateforme avec contrôle de concurrence"""
        async with semaphore:
            result = await self.check_platform(session, platform_name, platform_info)
            self.display_result(result)
            # Petit délai pour éviter le rate limiting
            await asyncio.sleep(0.2)
            return result
    
    def display_result(self, result):
        """Affiche le résultat d'une vérification"""
        platform = result["platform"]
        status = result["status"]
        
        if status == "found":
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {platform:20} - {Fore.GREEN}TROUVÉ{Style.RESET_ALL} ({result.get('response_time', '?')}s)")
        elif status == "not_found":
            print(f"{Fore.RED}✗{Style.RESET_ALL} {platform:20} - Non trouvé")
        elif status == "restricted":
            print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {platform:20} - Restreint/Accès refusé")
        elif status == "timeout":
            print(f"{Fore.RED}⏱{Style.RESET_ALL} {platform:20} - Délai dépassé")
        elif status == "rate_limited":
            print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {platform:20} - Limité (rate limit)")
        elif status == "manual":
            print(f"{Fore.BLUE}ℹ{Style.RESET_ALL} {platform:20} - Vérification manuelle")
        else:
            print(f"{Fore.RED}?{Style.RESET_ALL} {platform:20} - Erreur: {result.get('error', 'Inconnue')}")
    
    def generate_report(self, output_format="text"):
        """Génère un rapport des résultats"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_data = {
            "username": self.username,
            "timestamp": timestamp,
            "summary": {
                "total_platforms": len(self.results),
                "found": len(self.found),
                "not_found": len(self.not_found),
                "errors": len(self.errors)
            },
            "results": {
                "found": self.found,
                "not_found": self.not_found,
                "errors": self.errors
            }
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
        lines.append("RAPPORT RECONSCAN - RECHERCHE DE PSEUDO")
        lines.append("=" * 60)
        lines.append(f"Pseudo recherché: {data['username']}")
        lines.append(f"Date: {data['timestamp']}")
        lines.append("")
        lines.append("RÉSUMÉ")
        lines.append("-" * 40)
        lines.append(f"Total plateformes vérifiées: {data['summary']['total_platforms']}")
        lines.append(f"✅ Trouvés: {data['summary']['found']}")
        lines.append(f"❌ Non trouvés: {data['summary']['not_found']}")
        lines.append(f"⚠️  Erreurs/Manuels: {data['summary']['errors']}")
        lines.append("")
        
        if data['results']['found']:
            lines.append("PLATEFORMES TROUVÉES")
            lines.append("-" * 40)
            for result in data['results']['found']:
                lines.append(f"• {result['platform']}: {result['url']}")
            lines.append("")
        
        # Vérifier les résultats manuels dans la liste errors
        manual_results = [r for r in data['results'].get('errors', []) if r.get('status') == 'manual']
        if manual_results:
            lines.append("VÉRIFICATION MANUELLE REQUISE")
            lines.append("-" * 40)
            for result in manual_results:
                lines.append(f"• {result['platform']}: {result.get('note', 'N/A')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, filename=None, output_format="json"):
        """Sauvegarde le rapport dans un fichier"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reconscan_{self.username}_{timestamp}.{output_format}"
        
        report = self.generate_report(output_format)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename


def main():
    parser = argparse.ArgumentParser(
        description="ReconScan - Outil OSINT de recherche de pseudo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s username123
  %(prog)s john_doe --format json --output rapport.json
  %(prog)s test_user --timeout 15 --concurrent 5
        """
    )
    
    parser.add_argument(
        "username",
        help="Le pseudo à rechercher"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Format du rapport (défaut: text)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Nom du fichier de sortie (défaut: automatique)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=10,
        help="Délai d'attente en secondes (défaut: 10)"
    )
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=10,
        help="Nombre de requêtes concurrentes (défaut: 10)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Mode silencieux (pas d'affichage pendant la recherche)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Ne pas sauvegarder le rapport dans un fichier"
    )
    
    args = parser.parse_args()
    
    # Bannière
    if not args.quiet:
        print(f"""
{Fore.CYAN}
██████╗ ███████╗███████╗████████╗    ██████╗ ██████╗ ███████╗██████╗ 
██╔══██╗██╔════╝██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗██╔════╝██╔══██╗
██████╔╝█████╗  ███████╗   ██║       ██████╔╝██████╔╝█████╗  ██████╔╝
██╔══██╗██╔══╝  ╚════██║   ██║       ██╔═══╝ ██╔══██╗██╔══╝  ██╔══██╗
██║  ██║███████╗███████║   ██║       ██║     ██║  ██║███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}
{Fore.YELLOW}Outil OSINT de recherche de pseudo - v1.0{Style.RESET_ALL}
{Fore.YELLOW}Créé pour des fins éducatives et de sécurité légitime{Style.RESET_ALL}
        """)
    
    # Vérifier que le pseudo est valide
    if not args.username or len(args.username) < 2:
        print(f"{Fore.RED}Erreur: Le pseudo doit contenir au moins 2 caractères{Style.RESET_ALL}")
        sys.exit(1)
    
    # Exécuter la recherche
    scanner = ReconScan(
        username=args.username,
        timeout=args.timeout,
        max_concurrent=args.concurrent
    )
    
    try:
        asyncio.run(scanner.run_search())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Recherche interrompue par l'utilisateur{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Erreur lors de la recherche: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Afficher le résumé
    print(f"\n{Fore.CYAN}{'='*60}")
    print("RÉSULTATS DE LA RECHERCHE")
    print('='*60)
    print(f"{Fore.GREEN}✅ Plateformes trouvées: {len(scanner.found)}")
    print(f"{Fore.RED}❌ Non trouvées: {len(scanner.not_found)}")
    print(f"{Fore.YELLOW}⚠️  Erreurs/Manuelles: {len(scanner.errors)}")
    print(f"{Style.RESET_ALL}")
    
    # Sauvegarder le rapport
    if not args.no_save:
        try:
            filename = scanner.save_report(args.output, args.format)
            print(f"{Fore.GREEN}📄 Rapport sauvegardé: {filename}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Erreur lors de la sauvegarde: {e}{Style.RESET_ALL}")
    
    # Afficher les résultats trouvés
    if scanner.found:
        print(f"\n{Fore.GREEN}PLATEFORMES OÙ LE PSEUDO A ÉTÉ TROUVÉ:{Style.RESET_ALL}")
        for result in scanner.found:
            print(f"  • {result['platform']}: {result['url']}")
    
    print(f"\n{Fore.CYAN}Merci d'avoir utilisé ReconScan!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()