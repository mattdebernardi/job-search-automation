#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
import os
import sys

os.environ['PYTHONUNBUFFERED'] = '1'

RECIPIENT_EMAIL = "matthieu.debernardi@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(hours=72)

print(f"\n{'='*70}", flush=True)
print("🔍 JOB SEARCH AUTOMATION - DEBUG MODE", flush=True)
print(f"{'='*70}", flush=True)
print(f"⏰ Maintenant: {NOW.strftime('%d/%m/%Y %H:%M UTC')}", flush=True)
print(f"⏰ Cutoff (< 72h): {CUTOFF.strftime('%d/%m/%Y %H:%M UTC')}", flush=True)
print(f"{'='*70}\n", flush=True)

def parse_date(date_str):
    if not date_str: 
        return None
    date_str = date_str.strip()
    
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except:
        pass
    
    try:
        if date_str.endswith("Z"):
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return datetime.fromisoformat(date_str)
    except:
        pass
    
    return None

def fetch_rss(url):
    print(f"📡 Tentative fetch: {url[:80]}...", flush=True)
    try:
        resp = requests.get(url, timeout=15)
        print(f"   Status HTTP: {resp.status_code}", flush=True)
        
        if resp.status_code != 200:
            print(f"   ❌ Erreur HTTP {resp.status_code}\n", flush=True)
            return []
        
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")
        print(f"   ✓ {len(items)} items trouvés dans le XML", flush=True)
        
        offers = []
        for i, item in enumerate(items):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pubdate_str = item.findtext("pubDate", "").strip()
            
            if i < 3:  # Affiche les 3 premiers
                print(f"\n   Item {i+1}: {title[:60]}", flush=True)
                print(f"   Date: {pubdate_str[:50]}", flush=True)
            
            pubdate = parse_date(pubdate_str)
            
            if pubdate:
                age_hours = (NOW - pubdate).total_seconds() / 3600
                if i < 3:
                    print(f"   Âge: {age_hours:.1f}h", flush=True)
                
                if pubdate > CUTOFF:
                    if i < 3:
                        print(f"   ✅ GARDE (< 72h)\n", flush=True)
                    offers.append({"title": title, "link": link, "pubDate": pubdate})
                else:
                    if i < 3:
                        print(f"   ❌ REJETTE (> 72h)\n", flush=True)
        
        print(f"   ➡️  Résultat: {len(offers)}/{len(items)} offres valides\n", flush=True)
        return offers
    
    except Exception as e:
        print(f"   ❌ ERREUR: {type(e).__name__}: {e}\n", flush=True)
        return []

def send_email(subject, body):
    print(f"📧 Envoi email à {RECIPIENT_EMAIL}...", flush=True)
    
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("❌ Secrets manquants!", flush=True)
        return False
    
    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = RECIPIENT_EMAIL
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
        
        print("✅ Email envoyé avec succès\n", flush=True)
        return True
    
    except Exception as e:
        print(f"❌ Erreur email: {e}\n", flush=True)
        return False

def main():
    print("🌐 ÉTAPE 1: Récupération des flux RSS", flush=True)
    print("-" * 70 + "\n", flush=True)
    
    all_offers = []
    
    # URLs élargies (toute la France, pas juste Paris)
    urls = [
        "https://www.welcometothejungle.com/fr/rss/jobs?keywords=transformation&job_types=cdi",
        "https://fr.indeed.com/rss?q=transformation+digitale&sort=date",
    ]
    
    for url in urls:
        all_offers.extend(fetch_rss(url))
    
    print("\n" + "="*70, flush=True)
    print(f"📊 RÉSULTAT FINAL: {len(all_offers)} offre(s) trouvée(s)", flush=True)
    print("="*70 + "\n", flush=True)
    
    print("🌐 ÉTAPE 2: Génération du rapport", flush=True)
    print("-" * 70 + "\n", flush=True)
    
    if not all_offers:
        report = f"""
        <h1>❌ Aucune offre trouvée</h1>
        <p><strong>Date:</strong> {NOW.strftime('%d/%m/%Y à %H:%M UTC')}</p>
        <p>Aucune offre de transformation digitale trouvée datant de moins de 72 heures.</p>
        <p><em>Les offres trouvées sont probablement trop vieilles ou inexistantes.</em></p>
        """
    else:
        report = f"""
        <h1>✅ {len(all_offers)} Offre(s) trouvée(s)</h1>
        <p><strong>Période:</strong> Moins de 72 heures</p>
        <p><strong>Date du rapport:</strong> {NOW.strftime('%d/%m/%Y à %H:%M UTC')}</p>
        <hr>
        <ul>
        """
        for i, offer in enumerate(all_offers, 1):
            date_str = offer['pubDate'].strftime('%d/%m/%Y à %Hh%M')
            report += f"<li><strong>[{i}] {offer['title']}</strong><br>Date: {date_str}<br><a href='{offer['link']}'>Voir l'offre</a></li><hr>"
        
        report += "</ul>"
    
    subject = f"Recherche Offres Transformation Digitale — {NOW.strftime('%d %b %Y')}"
    
    print("📧 ÉTAPE 3: Envoi de l'email", flush=True)
    print("-" * 70 + "\n", flush=True)
    
    send_email(subject, report)
    
    print("="*70, flush=True)
    print("✅ EXÉCUTION TERMINÉE", flush=True)
    print("="*70 + "\n", flush=True)

if __name__ == "__main__":
    main()
