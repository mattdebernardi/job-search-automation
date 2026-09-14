#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET

urls = [
    "https://www.welcometothejungle.com/fr/rss/jobs?keywords=transformation&job_types=cdi",
    "https://fr.indeed.com/rss?q=transformation+digitale&sort=date",
]

for url in urls:
    print(f"\n{'='*80}")
    print(f"TEST: {url[:70]}...")
    print(f"{'='*80}")
    
    try:
        resp = requests.get(url, timeout=15)
        print(f"✓ HTTP {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type', 'unknown')}")
        print(f"Content length: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            print(f"✓ XML valide: {len(items)} items")
            
            if items:
                print("\n📝 PREMIERS ITEMS:")
                for i, item in enumerate(items[:3]):
                    title = item.findtext("title", "N/A")
                    pubdate = item.findtext("pubDate", "N/A")
                    print(f"\n  [{i+1}] {title[:60]}")
                    print(f"      Date: {pubdate}")
        else:
            print(f"❌ Erreur HTTP {resp.status_code}")
            print(f"Contenu: {resp.text[:500]}")
    
    except Exception as e:
        print(f"❌ ERREUR: {type(e).__name__}: {e}")

print(f"\n{'='*80}")
print("✅ Test terminé")
print(f"{'='*80}\n")
