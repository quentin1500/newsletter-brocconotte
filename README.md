# Newsletter Brocconotte

Générateur et envoi de newsletters HTML pour l’équipe Brocconotte.

## TL;DR (mode rapide)

1. Créer une nouvelle édition dans `content/YYYY-MM-DD/` (voir structure ci‑dessous)
2. Générer la newsletter :
	- `python scripts/build_newsletter.py`
3. Envoyer la newsletter :
	- `python scripts/send_newsletter.py`

## Prérequis

- Python 3.11+
- Dépendances :
  - `pip install -r requirements.txt`

## Structure du contenu

Chaque édition est un dossier dans `content/` :

```
content/
  2025-02-10/
	 meta.yml
	 intro.md
	 article-1.md
	 article-2.md
	 images/
		photo1.jpg
		photo2.png
```

### `meta.yml`

```yml
title: "Newsletter #1 – Lancement"
date: "2026-02-01"
```

### `intro.md`

Le texte d’introduction (Markdown). Laisse une ligne vide avant les listes.

### `article*.md`

Chaque article est un fichier Markdown. Les images référencées doivent être dans `images/`.

Exemple :

```md
![image](images/photo1.jpg)
```

## Génération HTML

```bash
python scripts/build_newsletter.py
```

- Génère `dist/YYYY-MM-DD.html`
- Redimensionne les images du dossier `images/` (largeur max 600px)
- Remplace les chemins d’images par des URLs absolues (GitHub Pages)

### Générer une édition spécifique

```bash
python scripts/build_newsletter.py 2025-02-10
```

## Envoi par email (local)

Configurer `.env` (ne pas versionner) :

```
NEWSLETTER_EMAIL=ton-email@gmail.com
NEWSLETTER_PASSWORD=mot-de-passe-app
```

Puis :

```bash
python scripts/send_newsletter.py
```

Par défaut, le script envoie en BCC à la liste définie dans `send_newsletter.py`.

## Envoi via GitHub Actions

Workflow manuel : **Send Newsletter**.

1. Ajouter les secrets (ou environnement dédié) :
	- `NEWSLETTER_EMAIL`
	- `NEWSLETTER_PASSWORD`
2. Lancer l’action :
	- Actions → Send Newsletter → Run workflow

Optionnel : fournir l’`issue` à envoyer.

## Dépannage rapide

- **Accents cassés** : exécuter `build_newsletter.py` après avoir corrigé les fichiers (UTF‑8).
- **Images non affichées** : vérifier que les images sont dans `content/<issue>/images/`.
- **Erreur Gmail** : utiliser un **App Password** (2FA requis) : https://myaccount.google.com/apppasswords

## Fichiers importants

- Template email : [templates/newsletter.html](templates/newsletter.html)
- Script build : [scripts/build_newsletter.py](scripts/build_newsletter.py)
- Script envoi : [scripts/send_newsletter.py](scripts/send_newsletter.py)

## Notes

- Les styles HTML sont simplifiés pour compatibilité Outlook.
- Le GIF est intégré en haut du template.
