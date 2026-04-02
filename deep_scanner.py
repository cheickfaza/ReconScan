#!/usr/bin/env python3
"""
Deep Scanner Module - Analyse approfondie des profils et mode deep scan
Inclut l'analyse des profils, détection de technologies, et extraction de métadonnées
"""

import asyncio
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

init(autoreset=True)


class DeepScanner:
    """Scanner approfondi pour analyse détaillée des profils"""
    
    def __init__(self, urls, timeout=15):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.timeout = timeout
        self.results = []
        
    async def scan_url(self, session, url):
        """Analyse approfondie d'une URL"""
        result = {
            "url": url,
            "status": "unknown",
            "profile_data": {},
            "technologies": [],
            "metadata": {},
            "files_found": [],
            "errors": []
        }
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True) as response:
                html = await response.text()
                result["status"] = response.status
                result["http_headers"] = dict(response.headers)
                
                # Analyse du contenu
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraction des données de profil
                result["profile_data"] = await self._extract_profile_data(soup, url)
                
                # Détection des technologies
                result["technologies"] = await self._detect_technologies(soup, response.headers, html)
                
                # Extraction des métadonnées
                result["metadata"] = await self._extract_metadata(soup)
                
                # Vérification des fichiers spéciaux
                result["files_found"] = await self._check_special_files(session, url)
                
        except asyncio.TimeoutError:
            result["errors"].append("Timeout")
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    async def _extract_profile_data(self, soup, url):
        """Extrait les données de profil d'une page"""
        data = {
            "title": "",
            "description": "",
            "author": "",
            "image": "",
            "bio": "",
            "links": [],
            "social_links": [],
            "creation_date": None,
            "followers": None,
            "following": None,
            "posts_count": None
        }
        
        try:
            # Titre
            title_tag = soup.find('title')
            if title_tag:
                data["title"] = title_tag.get_text().strip()
            
            # Description
            desc_tag = soup.find('meta', {'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                data["description"] = desc_tag['content'].strip()
            
            # OG Description
            og_desc = soup.find('meta', {'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                data["description"] = og_desc['content'].strip()
            
            # Auteur
            author_tag = soup.find('meta', {'name': 'author'})
            if author_tag and author_tag.get('content'):
                data["author"] = author_tag['content'].strip()
            
            # Image
            img_tag = soup.find('meta', {'property': 'og:image'})
            if img_tag and img_tag.get('content'):
                data["image"] = img_tag['content']
            
            # Bio (recherche dans les balises meta et les paragraphes)
            bio_patterns = [
                soup.find('meta', {'name': 'bio'}),
                soup.find('meta', {'name': 'description'}),
                soup.find('p', class_='bio'),
                soup.find('div', class_='bio'),
                soup.find('span', class_='bio')
            ]
            for pattern in bio_patterns:
                if pattern:
                    text = pattern.get_text().strip() if hasattr(pattern, 'get_text') else pattern.get('content', '').strip()
                    if text and len(text) > 10:
                        data["bio"] = text
                        break
            
            # Liens externes
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith(('http://', 'https://')):
                    data["links"].append({
                        "url": href,
                        "text": link.get_text().strip()[:100]
                    })
            
            # Réseaux sociaux
            social_platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'github', 'youtube', 'tiktok']
            for platform in social_platforms:
                social_link = soup.find('a', href=re.compile(rf'{platform}\.com', re.IGNORECASE))
                if social_link and social_link.get('href'):
                    data["social_links"].append({
                        "platform": platform,
                        "url": social_link['href']
                    })
            
            # Statistiques (followers, etc.)
            stats_patterns = {
                "followers": [r'(\d+[kKmM]?)\s*(?:followers|abonnés|seguidores)', r'followers[:\s]*(\d+[kKmM]?)'],
                "following": [r'(\d+[kKmM]?)\s*(?:following|abonnements|seguidos)', r'following[:\s]*(\d+[kKmM]?)'],
                "posts": [r'(\d+[kKmM]?)\s*(?:posts|publications|publicações)', r'posts[:\s]*(\d+[kKmM]?)']
            }
            
            text_content = soup.get_text()
            for key, patterns in stats_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE)
                    if match:
                        data[key] = match.group(1)
                        break
            
        except Exception as e:
            data["extraction_error"] = str(e)
        
        return data
    
    async def _detect_technologies(self, soup, headers, html):
        """Détecte les technologies utilisées par le site"""
        technologies = []
        
        try:
            # Détection par en-têtes HTTP
            if 'x-powered-by' in headers:
                technologies.append({
                    "name": headers['x-powered-by'],
                    "type": "server",
                    "source": "header"
                })
            
            if 'server' in headers:
                technologies.append({
                    "name": headers['server'],
                    "type": "webserver",
                    "source": "header"
                })
            
            # Détection par balises meta
            generator = soup.find('meta', {'name': 'generator'})
            if generator and generator.get('content'):
                technologies.append({
                    "name": generator['content'],
                    "type": "cms",
                    "source": "meta"
                })
            
            # Détection par classes CSS/JS
            tech_patterns = {
                "WordPress": r'wp-|wordpress',
                "React": r'react|react-dom',
                "Vue.js": r'vue|vuejs',
                "Angular": r'angular|ng-',
                "jQuery": r'jquery',
                "Bootstrap": r'bootstrap|bs-',
                "Tailwind CSS": r'tailwind',
                "Django": r'django',
                "Flask": r'flask',
                "Laravel": r'laravel',
                "Next.js": r'next',
                "Nuxt.js": r'nuxt'
            }
            
            for tech, pattern in tech_patterns.items():
                if re.search(pattern, html, re.IGNORECASE):
                    technologies.append({
                        "name": tech,
                        "type": "framework",
                        "source": "code"
                    })
            
            # Détection des scripts
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                src = script.get('src', '')
                if 'google-analytics' in src:
                    technologies.append({"name": "Google Analytics", "type": "analytics", "source": "script"})
                if 'googletagmanager' in src:
                    technologies.append({"name": "Google Tag Manager", "type": "tag-manager", "source": "script"})
            
        except Exception as e:
            technologies.append({"name": f"Error: {str(e)}", "type": "error", "source": "detection"})
        
        return technologies
    
    async def _extract_metadata(self, soup):
        """Extrait les métadonnées de la page"""
        metadata = {
            "language": None,
            "charset": None,
            "viewport": None,
            "robots": None,
            "canonical": None,
            "og_data": {},
            "twitter_data": {},
            "json_ld": []
        }
        
        try:
            # Langue
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                metadata["language"] = html_tag['lang']
            
            # Charset
            charset = soup.find('meta', {'charset': True})
            if charset:
                metadata["charset"] = charset['charset']
            
            # Viewport
            viewport = soup.find('meta', {'name': 'viewport'})
            if viewport and viewport.get('content'):
                metadata["viewport"] = viewport['content']
            
            # Robots
            robots = soup.find('meta', {'name': 'robots'})
            if robots and robots.get('content'):
                metadata["robots"] = robots['content']
            
            # Canonical URL
            canonical = soup.find('link', {'rel': 'canonical'})
            if canonical and canonical.get('href'):
                metadata["canonical"] = canonical['href']
            
            # Open Graph data
            og_tags = soup.find_all('meta', {'property': re.compile(r'^og:')})
            for tag in og_tags:
                prop = tag.get('property', '').replace('og:', '')
                content = tag.get('content', '')
                if prop and content:
                    metadata["og_data"][prop] = content
            
            # Twitter Card data
            twitter_tags = soup.find_all('meta', {'name': re.compile(r'^twitter:')})
            for tag in twitter_tags:
                name = tag.get('name', '').replace('twitter:', '')
                content = tag.get('content', '')
                if name and content:
                    metadata["twitter_data"][name] = content
            
            # JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    metadata["json_ld"].append(data)
                except (json.JSONDecodeError, TypeError):
                    pass
            
        except Exception as e:
            metadata["extraction_error"] = str(e)
        
        return metadata
    
    async def _check_special_files(self, session, url):
        """Vérifie la présence de fichiers spéciaux"""
        files_found = []
        special_files = [
            'robots.txt',
            'sitemap.xml',
            'sitemap.xml.gz',
            '.well-known/security.txt',
            'humans.txt',
            'ads.txt',
            'feed.xml',
            'rss.xml',
            'atom.xml'
        ]
        
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            for file in special_files:
                file_url = urljoin(base_url, file)
                try:
                    async with session.get(file_url, timeout=5) as response:
                        if response.status == 200:
                            content = await response.text()
                            files_found.append({
                                "file": file,
                                "url": file_url,
                                "size": len(content),
                                "exists": True
                            })
                except:
                    pass
            
        except Exception as e:
            files_found.append({"error": str(e)})
        
        return files_found
    
    async def run_scan(self):
        """Exécute le scan approfondi"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.scan_url(session, url) for url in self.urls]
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.results
    
    def generate_report(self, output_format="json"):
        """Génère un rapport des résultats"""
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_urls": len(self.results),
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
        lines.append("RAPPORT DEEP SCAN - ReconScan")
        lines.append("=" * 60)
        lines.append(f"Date: {data['timestamp']}")
        lines.append(f"URLs analysées: {data['total_urls']}")
        lines.append("")
        
        for result in data['results']:
            lines.append(f"\nURL: {result.get('url', 'Unknown')}")
            lines.append("-" * 40)
            
            # Statut
            lines.append(f"Statut HTTP: {result.get('status', 'Unknown')}")
            
            # Données de profil
            profile = result.get('profile_data', {})
            if profile:
                lines.append("\nDONNÉES DE PROFIL:")
                if profile.get('title'):
                    lines.append(f"  Titre: {profile['title']}")
                if profile.get('description'):
                    lines.append(f"  Description: {profile['description'][:100]}...")
                if profile.get('bio'):
                    lines.append(f"  Bio: {profile['bio'][:100]}...")
                if profile.get('image'):
                    lines.append(f"  Image: {profile['image']}")
                if profile.get('followers'):
                    lines.append(f"  Followers: {profile['followers']}")
                if profile.get('social_links'):
                    lines.append("  Réseaux sociaux:")
                    for social in profile['social_links']:
                        lines.append(f"    - {social['platform']}: {social['url']}")
            
            # Technologies
            techs = result.get('technologies', [])
            if techs:
                lines.append("\nTECHNOLOGIES DÉTECTÉES:")
                for tech in techs:
                    lines.append(f"  - {tech.get('name', 'Unknown')} ({tech.get('type', 'N/A')})")
            
            # Fichiers spéciaux
            files = result.get('files_found', [])
            if files:
                lines.append("\nFICHIERS SPÉCIAUX TROUVÉS:")
                for file in files:
                    if file.get('exists'):
                        lines.append(f"  ✓ {file['file']} ({file['url']})")
            
            # Erreurs
            errors = result.get('errors', [])
            if errors:
                lines.append("\nERREURS:")
                for error in errors:
                    lines.append(f"  ⚠️ {error}")
        
        return "\n".join(lines)
    
    def save_report(self, filename=None, output_format="json"):
        """Sauvegarde le rapport"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"deep_scan_{timestamp}.{output_format}"
        
        report = self.generate_report(output_format)
        
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
        print(f"{Fore.RED}Usage: python deep_scanner.py <url> [url2 ...]{Style.RESET_ALL}")
        sys.exit(1)
    
    urls = sys.argv[1:]
    scanner = DeepScanner(urls)
    
    print(f"{Fore.CYAN}🔍 Deep Scan en cours...{Style.RESET_ALL}")
    results = await scanner.run_scan()
    
    # Sauvegarder le rapport
    filename = scanner.save_report()
    print(f"\n{Fore.GREEN}📄 Rapport sauvegardé: {filename}{Style.RESET_ALL}")
    
    # Afficher le rapport texte
    print("\n" + scanner.generate_report("text"))


if __name__ == "__main__":
    asyncio.run(main())