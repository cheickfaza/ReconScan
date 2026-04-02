#!/usr/bin/env python3
"""
Username Correlator Module - Recherche inversée de pseudo
Trouve d'autres pseudos utilisés par la même personne et corrèle les comptes
"""

import asyncio
import re
import json
import math
from datetime import datetime
from pathlib import Path
from collections import Counter

import aiohttp
from colorama import init, Fore, Style

init(autoreset=True)


class UsernameCorrelator:
    """Corrélateur de pseudos pour recherche inversée"""
    
    def __init__(self, username, timeout=10):
        self.username = username
        self.timeout = timeout
        self.related_usernames = set()
        self.correlated_accounts = []
        self.patterns = {}
        
    def calculate_similarity(self, name1, name2):
        """Calcule la similarité entre deux pseudos"""
        # Distance de Levenshtein simplifiée
        if len(name1) < len(name2):
            name1, name2 = name2, name1
        
        if len(name2) == 0:
            return 0
        
        previous_row = range(len(name2) + 1)
        for i, c1 in enumerate(name1):
            current_row = [i + 1]
            for j, c2 in enumerate(name2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        distance = previous_row[-1]
        max_len = max(len(name1), len(name2))
        similarity = 1 - (distance / max_len)
        
        return similarity
    
    def extract_username_variations(self, username):
        """Extrait les variations possibles d'un pseudo"""
        variations = set()
        
        # Nettoyer le pseudo
        clean = re.sub(r'[^a-zA-Z0-9_]', '', username.lower())
        
        # Variations communes
        prefixes = ['', 'the', 'real', 'official', 'mr', 'ms', 'dr', 'im', 'i_am']
        suffixes = ['', '1', '123', '007', 'x', 'xx', 'xxx', 'official', 'real', 'true', 'pro', 'hq']
        separators = ['_', '.', '-', '']
        
        for prefix in prefixes:
            for suffix in suffixes:
                for sep in separators:
                    if prefix or suffix:
                        variation = f"{prefix}{sep}{clean}{sep}{suffix}"
                        variations.add(variation)
        
        # Ajouter des variations avec chiffres
        for i in range(1, 100):
            variations.add(f"{clean}{i}")
            variations.add(f"{clean}_{i}")
        
        # Variations avec année
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            variations.add(f"{clean}{year}")
        
        return variations
    
    async def search_similar_usernames(self, session, platform_url, platform_name):
        """Recherche des pseudos similaires sur une plateforme"""
        results = []
        
        try:
            # Cette fonction est limitée car elle nécessite souvent une API
            # Nous utilisons des techniques de déduction basées sur les patterns
            variations = self.extract_username_variations(self.username)
            
            for variation in list(variations)[:20]:  # Limiter pour éviter le spam
                url = platform_url.format(variation)
                try:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            results.append({
                                "username": variation,
                                "platform": platform_name,
                                "url": url,
                                "similarity": self.calculate_similarity(self.username, variation)
                            })
                except:
                    pass
                
                await asyncio.sleep(0.1)  # Petit délai
            
        except Exception as e:
            results.append({"error": str(e)})
        
        return results
    
    async def analyze_username_pattern(self):
        """Analyse les patterns du pseudo"""
        self.patterns = {
            "base": re.sub(r'[^a-zA-Z0-9]', '', self.username.lower()),
            "length": len(self.username),
            "has_numbers": bool(re.search(r'\d', self.username)),
            "has_special": bool(re.search(r'[_\-.]', self.username)),
            "has_uppercase": bool(re.search(r'[A-Z]', self.username)),
            "word_pattern": self._extract_word_pattern(self.username),
            "common_words": self._extract_common_words(self.username),
            "number_pattern": self._extract_number_pattern(self.username)
        }
        
        return self.patterns
    
    def _extract_word_pattern(self, username):
        """Extrait le pattern de mots"""
        words = re.findall(r'[a-zA-Z]+', username)
        return words
    
    def _extract_common_words(self, username):
        """Extrait les mots communs du pseudo"""
        common_words = [
            'admin', 'user', 'test', 'demo', 'guest', 'anonymous',
            'ninja', 'hacker', 'coder', 'dev', 'root', 'master',
            'dark', 'light', 'shadow', 'fire', 'ice', 'storm',
            'cool', 'awesome', 'epic', 'pro', 'elite', 'legend'
        ]
        
        found = []
        lower = username.lower()
        for word in common_words:
            if word in lower:
                found.append(word)
        
        return found
    
    def _extract_number_pattern(self, username):
        """Extrait le pattern de nombres"""
        numbers = re.findall(r'\d+', username)
        if numbers:
            return {
                "numbers": numbers,
                "is_year": any(int(n) > 1990 and int(n) < 2100 for n in numbers),
                "is_sequence": any(n in ['123', '000', '111', '999', '666'] for n in numbers)
            }
        return None
    
    async def find_correlated_accounts(self, found_profiles):
        """Trouve des comptes corrélés à partir des profils trouvés"""
        correlated = []
        
        for profile in found_profiles:
            platform = profile.get('platform', '')
            url = profile.get('url', '')
            
            # Extraire le pseudo de l'URL
            extracted_username = self._extract_username_from_url(url, platform)
            if extracted_username:
                similarity = self.calculate_similarity(self.username, extracted_username)
                if similarity > 0.5:  # Seuil de similarité
                    correlated.append({
                        "platform": platform,
                        "username": extracted_username,
                        "url": url,
                        "similarity": similarity,
                        "same_person_likelihood": self._calculate_likelihood(profile)
                    })
        
        return correlated
    
    def _extract_username_from_url(self, url, platform):
        """Extrait le pseudo d'une URL"""
        patterns = {
            "GitHub": r'github\.com/([^/]+)',
            "Twitter/X": r'twitter\.com/([^/]+)|nitter\.net/([^/]+)',
            "Reddit": r'reddit\.com/user/([^/]+)',
            "Instagram": r'instagram\.com/([^/]+)',
            "GitLab": r'gitlab\.com/([^/]+)',
            "Dev.to": r'dev\.to/([^/]+)',
            "CodePen": r'codepen\.io/([^/]+)',
            "Steam": r'steamcommunity\.com/id/([^/]+)',
            "Twitch": r'twitch\.tv/([^/]+)',
        }
        
        pattern = patterns.get(platform)
        if pattern:
            match = re.search(pattern, url)
            if match:
                return match.group(1) if match.lastindex == 1 else match.group(2)
        
        # Pattern générique
        match = re.search(r'/([^/]+?)(?:/|$)', url)
        if match:
            return match.group(1)
        
        return None
    
    def _calculate_likelihood(self, profile):
        """Calcule la probabilité que ce soit la même personne"""
        likelihood = 0.5  # Base
        
        # Facteurs augmentant la probabilité
        if profile.get('response_time'):
            likelihood += 0.1
        
        # Analyse du profil pour des indices supplémentaires
        # (à implémenter avec deep_scanner)
        
        return min(likelihood, 1.0)
    
    async def run_correlation(self, found_profiles=None):
        """Exécute la corrélation de pseudos"""
        print(f"\n{Fore.CYAN}🔄 Analyse des patterns de pseudo: {self.username}{Style.RESET_ALL}")
        
        # Analyser le pattern
        patterns = await self.analyze_username_pattern()
        
        print(f"{Fore.GREEN}✓ Pattern de base: {patterns['base']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Longueur: {patterns['length']} caractères{Style.RESET_ALL}")
        if patterns['common_words']:
            print(f"{Fore.GREEN}✓ Mots communs: {', '.join(patterns['common_words'])}{Style.RESET_ALL}")
        
        # Générer des variations
        variations = self.extract_username_variations(self.username)
        self.related_usernames = variations
        
        print(f"{Fore.GREEN}✓ {len(variations)} variations générées{Style.RESET_ALL}")
        
        # Si des profils sont fournis, analyser les corrélations
        if found_profiles:
            print(f"\n{Fore.CYAN}🔗 Analyse des corrélations...{Style.RESET_ALL}")
            self.correlated_accounts = await self.find_correlated_accounts(found_profiles)
            
            if self.correlated_accounts:
                print(f"{Fore.GREEN}✓ {len(self.correlated_accounts)} comptes corrélés trouvés{Style.RESET_ALL}")
        
        return {
            "original_username": self.username,
            "patterns": patterns,
            "variations_count": len(variations),
            "variations": list(variations)[:50],  # Limiter l'affichage
            "correlated_accounts": self.correlated_accounts
        }
    
    def generate_report(self, output_format="json"):
        """Génère un rapport des corrélations"""
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_username": self.username,
            "patterns": self.patterns,
            "related_usernames_count": len(self.related_usernames),
            "related_usernames": list(self.related_usernames)[:100],
            "correlated_accounts": self.correlated_accounts
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
        lines.append("RAPPORT DE CORRÉLATION DE PSEUDO - ReconScan")
        lines.append("=" * 60)
        lines.append(f"Pseudo original: {data['original_username']}")
        lines.append(f"Date: {data['timestamp']}")
        lines.append("")
        
        # Patterns
        lines.append("ANALYSE DU PSEUDO")
        lines.append("-" * 40)
        if data['patterns']:
            lines.append(f"Pattern de base: {data['patterns'].get('base', 'N/A')}")
            lines.append(f"Longueur: {data['patterns'].get('length', 'N/A')}")
            if data['patterns'].get('common_words'):
                lines.append(f"Mots communs: {', '.join(data['patterns']['common_words'])}")
            if data['patterns'].get('number_pattern'):
                np = data['patterns']['number_pattern']
                lines.append(f"Nombres: {np.get('numbers', [])}")
                if np.get('is_year'):
                    lines.append("  → Contient une année probable")
                if np.get('is_sequence'):
                    lines.append("  → Contient une séquence commune")
        lines.append("")
        
        # Variations
        lines.append(f"VARIATIONS POSSIBLES ({len(data['related_usernames'])} trouvées)")
        lines.append("-" * 40)
        for i, variation in enumerate(data['related_usernames'][:30]):
            similarity = self.calculate_similarity(self.username, variation)
            lines.append(f"  {i+1}. {variation} (similarité: {similarity:.0%})")
        if len(data['related_usernames']) > 30:
            lines.append(f"  ... et {len(data['related_usernames']) - 30} autres")
        lines.append("")
        
        # Comptes corrélés
        if data['correlated_accounts']:
            lines.append("COMPTES CORRÉLÉS TROUVÉS")
            lines.append("-" * 40)
            for account in data['correlated_accounts']:
                lines.append(f"  • {account['platform']}: {account['username']}")
                lines.append(f"    URL: {account['url']}")
                lines.append(f"    Similarité: {account['similarity']:.0%}")
                lines.append(f"    Probabilité même personne: {account['same_person_likelihood']:.0%}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, filename=None, output_format="json"):
        """Sauvegarde le rapport"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"username_correlation_{self.username}_{timestamp}.{output_format}"
        
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
        print(f"{Fore.RED}Usage: python username_correlator.py <username>{Style.RESET_ALL}")
        sys.exit(1)
    
    username = sys.argv[1]
    correlator = UsernameCorrelator(username)
    
    print(f"{Fore.CYAN}🔄 Analyse de corrélation en cours...{Style.RESET_ALL}")
    results = await correlator.run_correlation()
    
    # Sauvegarder le rapport
    filename = correlator.save_report()
    print(f"\n{Fore.GREEN}📄 Rapport sauvegardé: {filename}{Style.RESET_ALL}")
    
    # Afficher le rapport texte
    print("\n" + correlator.generate_report("text"))


if __name__ == "__main__":
    asyncio.run(main())