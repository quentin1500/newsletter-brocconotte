from __future__ import annotations

from datetime import date
from pathlib import Path

META_TEMPLATE = """title: \"Newsletter #X – Titre\"
date: \"{date}\"
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

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    content_dir = root / "content"
    today_folder = content_dir / date.today().isoformat()
    today_folder.mkdir(parents=True, exist_ok=True)
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
