#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import re
import smtplib
from email.mime.text import MIMEText
import os

RECIPIENT_EMAIL = "matthieu.debernardi@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(hours=72)

def parse_date(date_str):
    if not date_str: return None
    date_str = date_str.strip()
    try: return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except: pass
    try:
        if date_str.endswith("Z"): return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return datetime.fromisoformat(date_str)
    except: pass
    if "il y a" in date_str.lower():
        match = re.search(r"(\d+)\s+(heure|jour)", date_str.lower())
        if match:
            count = int(match.group(1))
            if "heure" in match.group(2): return NOW - timedelta(hours=count)
    return None

def fetch_rss(url):
    try:
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        offers = []
        for item in root.findall(".//item"):
            title, link = item.findtext("title", "").strip(), item.findtext("link", "").strip()
            pub_date = parse_date(item.findtext("pubDate", "").strip())
            if title and link and pub_date and pub_date > CUTOFF:
                offers.append({"title": title, "link": link, "pubDate": pub_date, "source": "RSS"})
        return offers
    except: return []

def score_offer(offer):
    combined = offer["title"].lower()
    score = 2 + (2 if any(x in combined for x in ["mentor", "formation"]) else 0)
    score += 1 if any(x in combined for x in ["conception", "stratégie"]) else 0
    score += 1.5 if any(x in combined for x in ["adoption", "digital"]) else 0
    return min(score, 10)

def send_email(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD: return False
    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = RECIPIENT_EMAIL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
        print(f"✅ Email envoyé")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    all_offers = []
    for url in [
        "https://www.welcometothejungle.com/fr/rss/jobs?keywords=transformation%20digitale&locations=paris",
        "https://fr.indeed.com/rss?q=transformation+digitale&l=paris&sort=date",
    ]:
        all_offers.extend(fetch_rss(url))
    
    scored = [o for o in all_offers if score_offer(o) >= 5]
    report = f"<h1>Offres Transformation Digitale — {NOW.strftime('%d %b')}</h1><p>{len(scored)} offres trouvées</p>"
    for o in scored:
        report += f"<p><a href='{o['link']}'>{o['title']}</a></p>"
    
    send_email(f"Offres — {NOW.strftime('%d %b')}", report)

if __name__ == "__main__": main()
