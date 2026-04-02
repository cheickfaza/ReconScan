#!/usr/bin/env python3
"""
Advanced Exporter Module - Export HTML, CSV et rapports avancés
Génération de rapports interactifs avec graphiques
"""

import json
import csv
import io
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from colorama import init, Fore, Style

init(autoreset=True)


class AdvancedExporter:
    """Exporteur avancé pour rapports OSINT"""
    
    def __init__(self, data, report_type="username"):
        self.data = data
        self.report_type = report_type
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def export_json(self, filename=None):
        """Export en JSON"""
        if filename is None:
            filename = f"report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def export_csv(self, filename=None):
        """Export en CSV"""
        if filename is None:
            filename = f"report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = io.StringIO()
        
        if self.report_type == "username":
            self._export_username_csv(output)
        elif self.report_type == "email":
            self._export_email_csv(output)
        elif self.report_type == "deep_scan":
            self._export_deep_scan_csv(output)
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            f.write(output.getvalue())
        
        return filename
    
    def _export_username_csv(self, output):
        """Export CSV pour recherche par pseudo"""
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow(["Type", "Plateforme", "URL", "Statut", "Temps de réponse", "Notes"])
        
        # Résumé
        if 'summary' in self.data:
            writer.writerow(["RÉSUMÉ", "", "", "", "", ""])
            writer.writerow(["Total plateformes", self.data['summary'].get('total_platforms', ''), "", "", "", ""])
            writer.writerow(["Trouvés", self.data['summary'].get('found', ''), "", "", "", ""])
            writer.writerow(["Non trouvés", self.data['summary'].get('not_found', ''), "", "", "", ""])
            writer.writerow(["Erreurs", self.data['summary'].get('errors', ''), "", "", "", ""])
            writer.writerow(["", "", "", "", "", ""])
        
        # Résultats
        if 'results' in self.data:
            for status_type in ['found', 'not_found', 'errors']:
                results = self.data['results'].get(status_type, [])
                for result in results:
                    writer.writerow([
                        status_type.upper(),
                        result.get('platform', ''),
                        result.get('url', ''),
                        result.get('status', ''),
                        result.get('response_time', ''),
                        result.get('error', result.get('note', ''))
                    ])
    
    def _export_email_csv(self, output):
        """Export CSV pour recherche par email"""
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow(["Type", "Catégorie", "Détails", "URL", "Notes"])
        
        # Résumé
        if 'summary' in self.data:
            writer.writerow(["RÉSUMÉ", "", "", "", ""])
            writer.writerow(["Fuites de données", self.data['summary'].get('total_breaches', ''), "", "", ""])
            writer.writerow(["Gravatar trouvé", self.data['summary'].get('gravatar_found', ''), "", "", ""])
            writer.writerow(["Comptes sociaux", self.data['summary'].get('social_accounts_found', ''), "", "", ""])
            writer.writerow(["", "", "", "", ""])
        
        # Fuites
        if 'results' in self.data:
            breaches = self.data['results'].get('breaches', [])
            for breach in breaches:
                writer.writerow([
                    "FUITE",
                    breach.get('name', ''),
                    f"Date: {breach.get('breach_date', '')}",
                    "",
                    f"Données: {', '.join(breach.get('data_classes', []))}"
                ])
            
            # Gravatar
            gravatar = self.data['results'].get('gravatar', {})
            if gravatar.get('found'):
                writer.writerow([
                    "GRAVATAR",
                    gravatar.get('display_name', ''),
                    "",
                    gravatar.get('profile_url', ''),
                    gravatar.get('aboutme', '')[:100] if gravatar.get('aboutme') else ""
                ])
            
            # Comptes sociaux
            social_accounts = self.data['results'].get('social_accounts', [])
            for account in social_accounts:
                writer.writerow([
                    "RÉSEAU SOCIAL",
                    account.get('service', ''),
                    account.get('username', ''),
                    account.get('url', ''),
                    ""
                ])
    
    def _export_deep_scan_csv(self, output):
        """Export CSV pour deep scan"""
        writer = csv.writer(output)
        
        writer.writerow(["URL", "Statut", "Titre", "Description", "Technologies", "Fichiers trouvés"])
        
        if 'results' in self.data:
            for result in self.data['results']:
                profile = result.get('profile_data', {})
                techs = result.get('technologies', [])
                files = result.get('files_found', [])
                
                writer.writerow([
                    result.get('url', ''),
                    result.get('status', ''),
                    profile.get('title', ''),
                    profile.get('description', '')[:100] if profile.get('description') else '',
                    ', '.join([t.get('name', '') for t in techs]),
                    ', '.join([f.get('file', '') for f in files if f.get('exists')])
                ])
    
    def export_html(self, filename=None):
        """Export en HTML interactif"""
        if filename is None:
            filename = f"report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        if self.report_type == "username":
            html = self._generate_username_html()
        elif self.report_type == "email":
            html = self._generate_email_html()
        elif self.report_type == "deep_scan":
            html = self._generate_deep_scan_html()
        elif self.report_type == "correlation":
            html = self._generate_correlation_html()
        else:
            html = self._generate_username_html()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filename
    
    def _generate_username_html(self):
        """Génère un rapport HTML pour recherche par pseudo"""
        summary = self.data.get('summary', {})
        results = self.data.get('results', {})
        
        found = results.get('found', [])
        not_found = results.get('not_found', [])
        errors = results.get('errors', [])
        
        # Calculer les pourcentages
        total = summary.get('total_platforms', 1)
        found_pct = (len(found) / total * 100) if total > 0 else 0
        not_found_pct = (len(not_found) / total * 100) if total > 0 else 0
        errors_pct = (len(errors) / total * 100) if total > 0 else 0
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReconScan - Rapport {self.data.get('username', 'OSINT')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .stat-card.found {{ border-left: 4px solid #4CAF50; }}
        .stat-card.not-found {{ border-left: 4px solid #f44336; }}
        .stat-card.errors {{ border-left: 4px solid #ff9800; }}
        .stat-card .number {{ font-size: 2.5em; font-weight: bold; color: #667eea; }}
        .stat-card .label {{ color: #666; margin-top: 5px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .chart-container h2 {{ margin-bottom: 20px; color: #667eea; }}
        .results-section {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .results-section h2 {{ margin-bottom: 20px; color: #667eea; }}
        .result-item {{ padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid; }}
        .result-item.found {{ background: #f1f8f4; border-color: #4CAF50; }}
        .result-item.not-found {{ background: #fff5f5; border-color: #f44336; }}
        .result-item.error {{ background: #fff8f0; border-color: #ff9800; }}
        .result-item .platform {{ font-weight: bold; font-size: 1.1em; }}
        .result-item .url {{ color: #666; word-break: break-all; margin-top: 5px; }}
        .result-item .url a {{ color: #667eea; text-decoration: none; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 ReconScan - Rapport OSINT</h1>
            <p>Pseudo recherché: <strong>{self.data.get('username', 'N/A')}</strong></p>
            <p>Date: {self.timestamp}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card found">
                <div class="number">{len(found)}</div>
                <div class="label">✅ Plateformes trouvées</div>
            </div>
            <div class="stat-card not-found">
                <div class="number">{len(not_found)}</div>
                <div class="label">❌ Non trouvées</div>
            </div>
            <div class="stat-card errors">
                <div class="number">{len(errors)}</div>
                <div class="label">⚠️ Erreurs</div>
            </div>
            <div class="stat-card">
                <div class="number">{total}</div>
                <div class="label">📊 Total vérifié</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📊 Répartition des résultats</h2>
            <canvas id="resultsChart"></canvas>
        </div>
        
        <div class="results-section">
            <h2>✅ Plateformes trouvées ({len(found)})</h2>
            <table>
                <tr><th>Plateforme</th><th>URL</th><th>Temps de réponse</th></tr>
                {''.join(f'<tr><td>{r.get("platform", "")}</td><td><a href="{r.get("url", "")}" target="_blank">{r.get("url", "")}</a></td><td>{r.get("response_time", "N/A")}s</td></tr>' for r in found)}
            </table>
        </div>
        
        <div class="results-section">
            <h2>⚠️ Erreurs et limitations ({len(errors)})</h2>
            {''.join(f'<div class="result-item error"><div class="platform">{r.get("platform", "")}</div><div class="url">{r.get("error", r.get("note", "N/A"))}</div></div>' for r in errors)}
        </div>
        
        <div class="footer">
            <p>Généré par ReconScan v3.0 - Outil OSINT</p>
            <p><a href="https://github.com/cheickfaza/ReconScan">GitHub</a></p>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('resultsChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Trouvés', 'Non trouvés', 'Erreurs'],
                datasets: [{{
                    data: [{len(found)}, {len(not_found)}, {len(errors)}],
                    backgroundColor: ['#4CAF50', '#f44336', '#ff9800']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_email_html(self):
        """Génère un rapport HTML pour recherche par email"""
        summary = self.data.get('summary', {})
        results = self.data.get('results', {})
        
        breaches = results.get('breaches', [])
        gravatar = results.get('gravatar', {})
        social_accounts = results.get('social_accounts', [])
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReconScan - Rapport Email</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .card h2 {{ color: #f5576c; margin-bottom: 15px; }}
        .breach {{ padding: 15px; margin: 10px 0; background: #fff5f5; border-left: 4px solid #f44336; border-radius: 0 5px 5px 0; }}
        .breach h3 {{ color: #f44336; }}
        .breach .date {{ color: #666; font-size: 0.9em; }}
        .social-account {{ padding: 10px; margin: 5px 0; background: #f0f8ff; border-left: 4px solid #2196F3; }}
        .gravatar-profile {{ display: flex; align-items: center; gap: 20px; }}
        .gravatar-profile img {{ width: 100px; height: 100px; border-radius: 50%; }}
        .stat {{ display: inline-block; padding: 10px 20px; background: #f5576c; color: white; border-radius: 5px; margin: 5px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 ReconScan - Rapport Email</h1>
            <p>Email analysé: <strong>{self.data.get('email', 'N/A')}</strong></p>
            <p>Date: {self.timestamp}</p>
        </div>
        
        <div class="card">
            <h2>📊 Résumé</h2>
            <div class="stat">Fuites: {summary.get('total_breaches', 0)}</div>
            <div class="stat">Gravatar: {'✅' if summary.get('gravatar_found') else '❌'}</div>
            <div class="stat">Réseaux: {summary.get('social_accounts_found', 0)}</div>
        </div>
        
        {''.join(f'''
        <div class="card">
            <h2>⚠️ Fuites de données ({len(breaches)})</h2>
            {''.join(f'''<div class="breach">
                <h3>{b.get('name', 'Unknown')}</h3>
                <p class="date">Date: {b.get('breach_date', 'Unknown')}</p>
                <p>Données compromises: {', '.join(b.get('data_classes', []))}</p>
            </div>''' for b in breaches)}
        </div>''' if breaches else '')}
        
        {''.join(f'''
        <div class="card">
            <h2>👤 Profil Gravatar</h2>
            <div class="gravatar-profile">
                <img src="{gravatar.get('thumbnail', '')}" alt="Gravatar">
                <div>
                    <h3>{gravatar.get('display_name', 'N/A')}</h3>
                    <p>{gravatar.get('aboutme', '')[:200]}</p>
                    <p><a href="{gravatar.get('profile_url', '#')}">Voir le profil</a></p>
                </div>
            </div>
        </div>''' if gravatar.get('found') else '')}
        
        {''.join(f'''
        <div class="card">
            <h2>🌐 Comptes sociaux découverts ({len(social_accounts)})</h2>
            {''.join(f'''<div class="social-account">
                <strong>{a.get('service', 'Unknown')}</strong>: {a.get('username', 'N/A')}
                <br><a href="{a.get('url', '#')}">{a.get('url', '#')}</a>
            </div>''' for a in social_accounts)}
        </div>''' if social_accounts else '')}
        
        <div class="footer">
            <p>Généré par ReconScan v3.0 - Outil OSINT</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_deep_scan_html(self):
        """Génère un rapport HTML pour deep scan"""
        results = self.data.get('results', [])
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReconScan - Deep Scan Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #0f3460, #16213e); padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .url-card {{ background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .url-card h2 {{ color: #00d9ff; margin-bottom: 15px; }}
        .section {{ margin: 15px 0; }}
        .section h3 {{ color: #00d9ff; margin-bottom: 10px; font-size: 1em; }}
        .tag {{ display: inline-block; padding: 5px 10px; background: #0f3460; border-radius: 3px; margin: 3px; font-size: 0.9em; }}
        .tag.tech {{ background: #e94560; }}
        .tag.file {{ background: #0f3460; border: 1px solid #00d9ff; }}
        .meta {{ color: #888; font-size: 0.9em; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 ReconScan - Deep Scan Report</h1>
            <p>Date: {self.timestamp}</p>
            <p>URLs analysées: {len(results)}</p>
        </div>
        
        {''.join(f'''
        <div class="url-card">
            <h2>{r.get('url', 'Unknown')}</h2>
            <p class="meta">Statut HTTP: {r.get('status', 'Unknown')}</p>
            
            <div class="section">
                <h3>📋 Profil</h3>
                {''.join(f'<span class="tag">{r.get("profile_data", {}).get("title", "")}</span>' if r.get('profile_data', {}).get('title') else '')}
                <p>{r.get('profile_data', {}).get('description', '')[:200]}</p>
            </div>
            
            <div class="section">
                <h3>⚙️ Technologies</h3>
                {''.join(f'<span class="tag tech">{t.get("name", "")}</span>' for t in r.get('technologies', []))}
            </div>
            
            <div class="section">
                <h3>📁 Fichiers spéciaux</h3>
                {''.join(f'<span class="tag file">✓ {f.get("file", "")}</span>' for f in r.get('files_found', []) if f.get('exists'))}
            </div>
        </div>''' for r in results)}
        
        <div class="footer">
            <p>ReconScan v3.0</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_correlation_html(self):
        """Génère un rapport HTML pour corrélation de pseudos"""
        related = self.data.get('related_usernames', [])
        correlated = self.data.get('correlated_accounts', [])
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>ReconScan - Username Correlation</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #667eea; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        .similarity {{ font-weight: bold; }}
        .high {{ color: #4CAF50; }}
        .medium {{ color: #ff9800; }}
        .low {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🔄 Username Correlation Report</h1>
            <p>Original: <strong>{self.data.get('original_username', 'N/A')}</strong></p>
            <p>Date: {self.timestamp}</p>
        </div>
        
        <div class="card">
            <h2>📊 Patterns analysés</h2>
            <p>Base: {self.data.get('patterns', {}).get('base', 'N/A')}</p>
            <p>Variations générées: {len(related)}</p>
        </div>
        
        <div class="card">
            <h2>🔗 Comptes corrélés ({len(correlated)})</h2>
            <table>
                <tr><th>Plateforme</th><th>Pseudo</th><th>Similarité</th><th>URL</th></tr>
                {''.join(f'<tr><td>{a.get("platform", "")}</td><td>{a.get("username", "")}</td><td class="similarity {"high" if a.get("similarity", 0) > 0.8 else "medium" if a.get("similarity", 0) > 0.6 else "low"}">{a.get("similarity", 0):.0%}</td><td><a href="{a.get("url", "#")}">{a.get("url", "#")}</a></td></tr>' for a in correlated)}
            </table>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def export_all(self, base_filename=None):
        """Export dans tous les formats"""
        if base_filename is None:
            base_filename = f"report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        files = {}
        files['json'] = self.export_json(f"{base_filename}.json")
        files['csv'] = self.export_csv(f"{base_filename}.csv")
        files['html'] = self.export_html(f"{base_filename}.html")
        
        return files


async def main():
    """Test de l'exporteur"""
    import sys
    
    # Exemple de données
    test_data = {
        "username": "test_user",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_platforms": 10,
            "found": 3,
            "not_found": 5,
            "errors": 2
        },
        "results": {
            "found": [
                {"platform": "GitHub", "url": "https://github.com/test_user", "response_time": 0.5},
                {"platform": "Reddit", "url": "https://reddit.com/user/test_user", "response_time": 0.3}
            ],
            "not_found": [],
            "errors": []
        }
    }
    
    exporter = AdvancedExporter(test_data, "username")
    files = exporter.export_all()
    
    print(f"{Fore.GREEN}✓ Rapports générés:{Style.RESET_ALL}")
    for fmt, path in files.items():
        print(f"  {fmt.upper()}: {path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())