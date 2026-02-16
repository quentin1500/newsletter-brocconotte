from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse

META_TEMPLATE = """title: \"Newsletter #X – Titre\"
date: \"{date}\"
"""

META_CANVAS_TEMPLATE = """title: \"Newsletter #X – Titre\"
date: \"{date}\"
type: canvas
"""

INTRO_TEMPLATE = """# Introduction

Écris ici l'introduction de la newsletter.

- Point 1
- Point 2
"""

ARTICLE_1_TEMPLATE = """# Titre de l'article 1

Ton contenu ici.

![image](images/placeholder.jpg)
"""

# Canvas type uses an image file instead of text template

def main() -> None:
    parser = argparse.ArgumentParser(description="Créer un dossier d'édition dans content/ ou planned-content/")
    parser.add_argument(
        "--type",
        choices=["normal", "canvas"],
        default="normal",
        help="Type d'édition à créer (normal ou canvas)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date du dossier au format YYYY-MM-DD (par défaut: date d'aujourd'hui)",
    )
    parser.add_argument(
        "--planned",
        action="store_true",
        help="Créer le dossier dans planned-content/ au lieu de content/",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    
    # Déterminer la date
    if args.date:
        issue_date = args.date
    else:
        issue_date = date.today().isoformat()
    
    # Déterminer le répertoire parent
    if args.planned:
        content_dir = root / "planned-content"
    else:
        content_dir = root / "content"
    
    today_folder = content_dir / issue_date
    today_folder.mkdir(parents=True, exist_ok=True)

    if args.type == "canvas":
        meta_path = today_folder / "meta.yaml"

        if not meta_path.exists():
            meta_path.write_text(META_CANVAS_TEMPLATE.format(date=date.today().isoformat()), encoding="utf-8")

        print("ℹ️  Ajoute ton image Canvas dans le dossier (image.jpg recommandé)")
    else:
        images_dir = today_folder / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        meta_path = today_folder / "meta.yml"
        intro_path = today_folder / "intro.md"
        article_1_path = today_folder / "article-1.md"

        if not meta_path.exists():
            meta_path.write_text(META_TEMPLATE.format(date=date.today().isoformat()), encoding="utf-8")

        if not intro_path.exists():
            intro_path.write_text(INTRO_TEMPLATE, encoding="utf-8")

        if not article_1_path.exists():
            article_1_path.write_text(ARTICLE_1_TEMPLATE, encoding="utf-8")

    print(f"Dossier prêt: {today_folder}")


if __name__ == "__main__":
    main()
