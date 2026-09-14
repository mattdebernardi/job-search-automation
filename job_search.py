#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import re
import smtplib
from email.mime.text import MIMEText
import os
import sys

# Force flush
os.environ['PYTHONUNBUFFERED'] = '1'

RECIPIENT_EMAIL = "matthieu.debernardi@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(hours=72)

print(f"\n{'='*60}")
print("JOB SEARCH v3 - DEBUG VERSION")
print(f"{'='*60}", flush=True)
print(f"NOW: {NOW}", flush=True)
print(f"CUTOFF (< 72h): {CUTOFF}", flush=True)
print(f"GMAIL_USER: {GMAIL_USER}", flush=True)
print(f"GMAIL_PASSWORD: {'SET' if GMAIL_APP_PASSWORD else 'MISSING'}", flush=True)

def parse_date(date_str):
    if not date_str: 
        return None
    date_str = date_str.strip()
    
    # RFC 2822
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        print(f"  ✓ Date parsée (RFC 2822): {dt}", flush=True)
        return dt
    except:
        pass
    
    # ISO 8601
    try:
        if date_str.endswith("Z"):
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(date_str)
        print(f"  ✓ Date parsée (ISO): {dt}", flush=True)
        return dt
    except:
        pass
    
    print(f"  ❌ Date non parsée: {date_str[:50]}", flush=True)
    return None

def fetch_rss(url):
    print(f"\n📡 Fetching: {url[:70]}...", flush=True)
    try:
        resp = requests.get(url, timeout=10)
        print(f"  Status: {resp.status_code}", flush=True)
        
        if resp.status_code != 200:
            print(f"  ❌ HTTP {resp.status_code}", flush=True)
            return []
        
        root = ET.fromstring(resp.content)
        print(f"  ✓ XML parsed", flush=True)
        
        items = root.findall(".//item")
        print(f"  Found {len(items)} items", flush=True)
        
        offers = []
        for i, item in enumerate(items[:5]):  # Check first 5
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pubdate_str = item.findtext("pubDate", "").strip()
            
            print(f"    Item {i+1}: {title[:50]}", flush=True)
            print(f"      pubDate raw: {pubdate_str[:40]}", flush=True)
            
            pubdate = parse_date(pubdate_str)
            
            if pubdate:
                age = NOW - pubdate
                hours_old = age.total_seconds() / 3600
                print(f"      Age: {hours_old:.1f}h", flush=True)
                
                if pubdate > CUTOFF:
                    print(f"      ✅ KEEP (< 72h)", flush=True)
                    offers.append({"title": title, "link": link, "pubDate": pubdate})
                else:
                    print(f"      ❌ SKIP (> 72h)", flush=True)
            else:
                print(f"      ❌ No date", flush=True)
        
        print(f"  Result: {len(offers)} valid offers", flush=True)
        return offers
    
    except Exception as e:
        print(f"  ❌ ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return []

def send_email(subject, body):
    print(f"\n📧 Sending email...", flush=True)
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("❌ Missing credentials", flush=True)
        return False
    
    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = RECIPIENT_EMAIL
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
        
        print(f"✅ Email sent", flush=True)
        return True
    except Exception as e:
        print(f"❌ Email error: {e}", flush=True)
        return False

def main():
    all_offers = []
    
    urls = [
        "https://www.welcometothejungle.com/fr/rss/jobs?keywords=transformation%20digitale&locations=paris&job_types=cdi",
        "https://fr.indeed.com/rss?q=transformation+digitale&l=paris&sort=date",
    ]
    
    for url in urls:
        all_offers.extend(fetch_rss(url))
    
    print(f"\n{'='*60}", flush=True)
    print(f"TOTAL: {len(all_offers)} offers found", flush=True)
    print(f"{'='*60}", flush=True)
    
    if not all_offers:
        report = f"<h2>❌ Aucune offre trouvée pour {NOW.strftime('%d/%m/%Y')}</h2>"
    else:
        report = f"<h2>✅ {len(all_offers)} offres trouvées</h2><ul>"
        for o in all_offers:
            report += f"<li><a href='{o['link']}'>{o['title']}</a></li>"
        report += "</ul>"
    
    subject = f"Offres — {NOW.strftime('%d %b %Y')}"
    send_email(subject, report)
    
    print("\n✅ Done\n", flush=True)

if __name__ == "__main__":
    main()
