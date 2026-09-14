#!/usr/bin/env python3
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone

# Tentative d'import WebSearch (si disponible)
try:
    from anthropic import Anthropic
    client = Anthropic()
    HAS_ANTHROPIC = True
except:
    HAS_ANTHROPIC = False

RECIPIENT_EMAIL = "matthieu.debernardi@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOW = datetime.now(timezone.utc)

print(f"\n{'='*80}", flush=True)
print("🔍 JOB SEARCH v4 - WEBSEARCH + POST-PROCESSING", flush=True)
print(f"{'='*80}\n", flush=True)

def send_email(subject, body):
    """Envoie l'email avec les résultats."""
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
        
        print("✅ Email envoyé\n", flush=True)
        return True
    
    except Exception as e:
        print(f"❌ Erreur email: {e}\n", flush=True)
        return False

def main():
    print("⚠️  NOTE: RSS feeds ne fonctionnent pas (HTML au lieu de XML, 403, etc.)", flush=True)
    print("         Solution: Utiliser un service tiers (Zapier/Make) ou crawler personnel\n", flush=True)
    
    # Message d'alerte
    report = f"""
    <h1>⚠️ Problème de récupération des données</h1>
    
    <h2>Résumé</h2>
    <p><strong>Date du rapport:</strong> {NOW.strftime('%d/%m/%Y à %H:%M UTC')}</p>
    
    <h2>Problème identifié</h2>
    <p>Les sources RSS configurées <strong>ne retournent pas de contenu valide</strong> :</p>
    
    <ul>
        <li><strong>Welcome to the Jungle</strong> : Retourne HTML au lieu du RSS</li>
        <li><strong>Indeed</strong> : Retourne erreur 403 (accès bloqué)</li>
    </ul>
    
    <h2>Solution recommandée</h2>
    <p>Passer par un <strong>service tiers gratuit</strong> pour contourner ces blocages :</p>
    
    <ul>
        <li><strong>Make.com</strong> (ex Integromat) - Gratuit jusqu'à 100 ops/mois</li>
        <li><strong>Zapier</strong> - Gratuit jusqu'à 100 tasks/mois</li>
        <li><strong>GitHub Actions avec npm packages</strong> - Gratuit</li>
    </ul>
    
    <h2>Prochaines étapes</h2>
    <p>Tu veux configurer un service tiers ? Dis-moi lequel !</p>
    """
    
    subject = f"⚠️ Recherche d'offres — Problème technique — {NOW.strftime('%d %b %Y')}"
    send_email(subject, report)
    
    print("="*80, flush=True)
    print("✅ Rapport d'alerte envoyé", flush=True)
    print("="*80 + "\n", flush=True)

if __name__ == "__main__":
    main()
