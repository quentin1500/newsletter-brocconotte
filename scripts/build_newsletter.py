import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
import re
import sys
from PIL import Image


TEMPLATE_DIR = "templates"
DIST_DIR = "dist"
BASE_IMAGE_URL = "https://newsletter.brocconotte.fr/"
MAX_IMAGE_WIDTH = 600

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def load_meta(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_meta_path(issue_path):
    meta_yml = os.path.join(issue_path, "meta.yml")
    meta_yaml = os.path.join(issue_path, "meta.yaml")
    if os.path.exists(meta_yml):
        return meta_yml
    if os.path.exists(meta_yaml):
        return meta_yaml
    return meta_yml

def md_to_html(path):
    with open(path, "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())

def resize_images_in_issue(issue_path):
    """Redimensionne les images du dossier issue/images pour réduire la taille."""
    images_dir = os.path.join(issue_path, "images")
    print(f"🔍 Redimensionnement des images dans {images_dir}...")
    if not os.path.exists(images_dir):
        return
    
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            image_path = os.path.join(images_dir, filename)
            try:
                with Image.open(image_path) as img:
                    # Redimensionner si la largeur dépasse MAX_IMAGE_WIDTH
                    if img.width > MAX_IMAGE_WIDTH:
                        ratio = MAX_IMAGE_WIDTH / img.width
                        new_height = int(img.height * ratio)
                        img_resized = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)
                        
                        # Sauvegarder avec compression
                        if filename.lower().endswith(('.jpg', '.jpeg')):
                            img_resized.save(image_path, 'JPEG', quality=85, optimize=True)
                        else:
                            img_resized.save(image_path, optimize=True)
                        
                        print(f"Image redimensionnée : {filename} ({img.width}x{img.height} → {MAX_IMAGE_WIDTH}x{new_height})")
            except Exception as e:
                print(f"Erreur en redimensionnant {filename} : {e}")

def absolutize_image_paths(html, issue, content_type="content"):
    def repl(match):
        before = match.group(1)  # attributs avant src (ex: alt="image")
        src = match.group(2)      # valeur du src
        after = match.group(3)    # tout après le src (ex: /)
        if src.startswith("http"):
            absolute_url = src
        else:
            absolute_url = f'{BASE_IMAGE_URL}{content_type}/{issue}/{src}'
        return f'<img{before} src="{absolute_url}"{after}>'

    return re.sub(r'<img([^>]*?) src="([^"]+)"([^>]*)>', repl, html)

def build_newsletter(issue, content_type="content"):
    content_dir = "planned-content" if content_type == "planned" else "content"
    issue_path = os.path.join(content_dir, issue)
    meta = load_meta(get_meta_path(issue_path))
    issue_type = (meta.get("type") or "normal").strip().lower()

    # Redimensionner les images avant de construire la newsletter
    resize_images_in_issue(issue_path)

    if issue_type == "canvas":
        # Find image file in the issue directory
        image_file = None
        for file in os.listdir(issue_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_file = file
                break
        
        if not image_file:
            print(f"⚠️  Aucune image trouvée dans {issue_path}")
            sys.exit(1)
        
        # Create absolute URL for the image
        image_url = f"{BASE_IMAGE_URL}{content_dir}/{issue}/{image_file}"
        
        template = env.get_template("newsletter-canvas.html")
        html = template.render(
            title=meta["title"],
            date=meta["date"],
            image_url=image_url,
        )
    else:
        intro = md_to_html(os.path.join(issue_path, "intro.md"))

        articles_html = ""
        for file in sorted(os.listdir(issue_path)):
            if file.startswith("article") and file.endswith(".md"):
                article_html = md_to_html(os.path.join(issue_path, file))
                article_html = absolutize_image_paths(article_html, issue, content_dir)
                articles_html += article_html

        template = env.get_template("newsletter.html")
        html = template.render(
            title=meta["title"],
            date=meta["date"],
            intro=intro,
            articles=articles_html
        )

    os.makedirs(DIST_DIR, exist_ok=True)
    output_path = os.path.join(DIST_DIR, f"{issue}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Newsletter générée : {output_path}")

if __name__ == "__main__":
    # Récupérer l'issue depuis l'argument ou les variables d'environnement (GitHub Actions)
    issue = None
    content_type = "content"
    
    # 1. Vérifier l'argument en ligne de commande pour le type
    if len(sys.argv) > 2:
        content_type = sys.argv[2].strip().lower()
        if content_type not in ["planned", "content"]:
            content_type = "content"
            print(f"⚠️  Type de contenu invalide, utilisation de 'content'")
    
    # 2. Vérifier l'argument en ligne de commande pour l'issue
    if len(sys.argv) > 1:
        issue = sys.argv[1]
        if issue.strip():  # Si l'argument n'est pas vide
            print(f"📰 Building issue: {issue} (type: {content_type})")
        else:
            issue = None
    
    # 3. Vérifier la variable d'environnement (GitHub Actions)
    if not issue:
        issue = os.getenv("NEWSLETTER_ISSUE")
        if issue:
            print(f"📰 Building issue from env: {issue} (type: {content_type})")
    
    # 4. Si aucun issue spécifié, utiliser la dernière
    if not issue:
        content_dir = "planned-content" if content_type == "planned" else "content"
        issues = sorted(os.listdir(content_dir))
        if not issues:
            print(f"❌ Erreur : Aucune newsletter trouvée dans le dossier '{content_dir}'")
            sys.exit(1)
        issue = issues[-1]
        print(f"📰 Building latest issue: {issue} (type: {content_type})")
    
    # Vérifier que l'issue existe
    content_dir = "planned-content" if content_type == "planned" else "content"
    issue_path = os.path.join(content_dir, issue)
    if not os.path.isdir(issue_path):
        print(f"❌ Erreur : Issue non trouvée: {issue_path}")
        sys.exit(1)
    
    build_newsletter(issue, content_type)
    
    # Générer la liste des newsletters pour le site
    print("\n📋 Génération de la liste des newsletters...")
    import subprocess
    try:
        subprocess.run([sys.executable, "scripts/generate_newsletter_list.py"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️ Erreur lors de la génération de la liste (non bloquant)")
