#!/usr/bin/env python3
"""
Username Scanner Module - Recherche de présence par pseudo
"""

import asyncio
import time
from typing import Dict, List

import aiohttp
from colorama import init, Fore, Style

init(autoreset=True)

# Liste des plateformes à vérifier
PLATFORMS = {
    "GitHub": {"url": "https://api.github.com/users/{}", "type": "api", "status_code": 200},
    "Twitter/X": {"url": "https://nitter.net/{}", "type": "web", "status_code": 200},
    "Reddit": {"url": "https://www.reddit.com/user/{}", "type": "web", "status_code": 200},
    "Instagram": {"url": "https://www.instagram.com/{}/", "type": "web", "status_code": 200},
    "Facebook": {"url": "https://www.facebook.com/{}", "type": "web", "status_code": 200},
    "TikTok": {"url": "https://www.tiktok.com/@{}", "type": "web", "status_code": 200},
    "LinkedIn": {"url": "https://www.linkedin.com/in/{}", "type": "web", "status_code": 200},
    "GitLab": {"url": "https://gitlab.com/{}", "type": "web", "status_code": 200},
    "Stack Overflow": {"url": "https://stackoverflow.com/users/tagged/{}", "type": "web", "status_code": 200},
    "Dev.to": {"url": "https://dev.to/{}", "type": "web", "status_code": 200},
    "CodePen": {"url": "https://codepen.io/{}", "type": "web", "status_code": 200},
    "npm": {"url": "https://www.npmjs.com/~{}", "type": "web", "status_code": 200},
    "PyPI": {"url": "https://pypi.org/user/{}/", "type": "web", "status_code": 200},
    "HackTheBox": {"url": "https://www.hackthebox.com/profile/{}", "type": "web", "status_code": 200},
    "TryHackMe": {"url": "https://tryhackme.com/p/{}", "type": "web", "status_code": 200},
    "Bugcrowd": {"url": "https://bugcrowd.com/{}", "type": "web", "status_code": 200},
    "HackerOne": {"url": "https://hackerone.com/{}", "type": "web", "status_code": 200},
    "Steam": {"url": "https://steamcommunity.com/id/{}", "type": "web", "status_code": 200},
    "Twitch": {"url": "https://api.twitch.tv/helix/users?login={}", "type": "api", "status_code": 200},
    "YouTube": {"url": "https://www.youtube.com/@{}", "type": "web", "status_code": 200},
    "Pinterest": {"url": "https://www.pinterest.com/{}/", "type": "web", "status_code": 200},
    "SoundCloud": {"url": "https://soundcloud.com/{}", "type": "web", "status_code": 200},
    "Spotify": {"url": "https://open.spotify.com/user/{}", "type": "web", "status_code": 200},
    "Keybase": {"url": "https://keybase.io/{}", "type": "api", "status_code": 200},
    "Telegram": {"url": "https://t.me/{}", "type": "web", "status_code": 200},
    "Medium": {"url": "https://medium.com/@{}", "type": "web", "status_code": 200},
    "Tumblr": {"url": "https://{}.tumblr.com/", "type": "web", "status_code": 200},
    "VK": {"url": "https://vk.com/{}", "type": "web", "status_code": 200},
    "Mastodon": {"url": "https://mastodon.social/@{}", "type": "web", "status_code": 200},
    "Quora": {"url": "https://www.quora.com/profile/{}", "type": "web", "status_code": 200},
}


class UsernameScanner:
    """Scanner de pseudos"""
    
    def __init__(self, username: str, timeout: int = 10, max_concurrent: int = 10):
        self.username = username
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.results: List[Dict] = []
    
    async def check_platform(
        self,
        session: aiohttp.ClientSession,
        platform_name: str,
        platform_info: Dict,
        semaphore: asyncio.Semaphore
    ) -> Dict:
        """Vérifie une plateforme"""
        async with semaphore:
            url = platform_info["url"].format(self.username)
            result = {
                "platform": platform_name,
                "url": url,
                "status": "unknown",
                "response_time": None,
                "http_status": None,
                "error": None
            }
            
            try:
                start_time = time.time()
                async with session.get(url, allow_redirects=True, timeout=self.timeout) as response:
                    elapsed = time.time() - start_time
                    result["response_time"] = round(elapsed, 3)
                    result["http_status"] = response.status
                    
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
                result["error"] = "Délai dépassé"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
            
            return result
    
    async def run_search(self) -> List[Dict]:
        """Exécute la recherche sur toutes les plateformes"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for platform_name, platform_info in PLATFORMS.items():
                task = self.check_platform(session, platform_name, platform_info, semaphore)
                tasks.append(task)
            
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.results


async def main():
    """Test"""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python username_scanner.py <username>")
        sys.exit(1)
    
    scanner = UsernameScanner(sys.argv[1])
    results = await scanner.run_search()
    
    found = [r for r in results if isinstance(r, dict) and r.get("status") == "found"]
    print(f"\nFound {len(found)} platforms:")
    for r in found:
        print(f"  ✓ {r['platform']}: {r['url']}")


if __name__ == "__main__":
    asyncio.run(main())