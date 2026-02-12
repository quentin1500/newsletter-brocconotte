import os
import json
import re

DIST_DIR = "docs"
OUTPUT_FILE = os.path.join(DIST_DIR, "newsletters.json")

def extract_title_from_html(filepath):
    """Extrait le titre depuis le HTML."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'<title>(.*?)</title>', content)
            if match:
                return match.group(1)
    except:
        pass
    return None

def generate_newsletter_list():
    """Génère un fichier JSON listant toutes les newsletters."""
    newsletters = []
    
    if not os.path.exists(DIST_DIR):
        print(f"❌ Dossier {DIST_DIR} introuvable")
        return
    
    for filename in sorted(os.listdir(DIST_DIR), reverse=True):
        # Ignorer les fichiers non-HTML et les fichiers spéciaux
        if not filename.endswith('.html'):
            continue
        if filename in ['index.html', 'subscribe.html']:
            continue
        
        filepath = os.path.join(DIST_DIR, filename)
        
        # Extraire le titre
        title = extract_title_from_html(filepath)
        if not title:
            title = filename.replace('.html', '')
        
        # Extraire la date depuis le nom de fichier (format YYYY-MM-DD.html)
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.html', filename)
        date = date_match.group(1) if date_match else None
        
        newsletters.append({
            "filename": filename,
            "title": title,
            "date": date
        })
    
    # Écrire le JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(newsletters, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Liste générée : {len(newsletters)} newsletter(s)")
    print(f"   Fichier : {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_newsletter_list()
