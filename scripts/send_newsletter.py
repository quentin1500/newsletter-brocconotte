import os
import sys
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

SENDER_EMAIL = os.getenv("NEWSLETTER_EMAIL")
SENDER_PASSWORD = os.getenv("NEWSLETTER_PASSWORD")
RECIPIENT_EMAIL = "quentin.lagonotte@gmail.com"  # Destinataire fixe pour l'instant, peut être mis dans .env si besoin
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

DIST_DIR = "dist"


def send_newsletter(issue):
    """Envoie la newsletter HTML par email."""
    
    # Vérifier que les paramètres sont configurés
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("❌ Erreur : Variables d'environnement manquantes dans .env")
        print("   Vérifiez que NEWSLETTER_EMAIL, NEWSLETTER_PASSWORD et NEWSLETTER_RECIPIENT sont définis.")
        sys.exit(1)
    
    # Charger le fichier HTML
    html_path = os.path.join(DIST_DIR, f"{issue}.html")
    if not os.path.exists(html_path):
        print(f"❌ Erreur : Fichier HTML non trouvé : {html_path}")
        sys.exit(1)
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extraire le titre de la newsletter du HTML
    import re
    match = re.search(r'<title>(.*?)</title>', html_content)
    subject = match.group(1) if match else f"Newsletter {issue}"
    
    # Préparer l'email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    
    # Ajouter le contenu HTML
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    # Envoyer l'email
    try:
        print(f"📧 Connexion à {SMTP_SERVER}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        
        print(f"✅ Newsletter envoyée avec succès à {RECIPIENT_EMAIL}")
        print(f"   Sujet : {subject}")
    
    except smtplib.SMTPAuthenticationError:
        print("❌ Erreur d'authentification : Vérifiez vos identifiants Gmail")
        print("   💡 Pour Gmail, utilisez un 'App Password' si vous avez 2FA activé")
        sys.exit(1)
    
    except smtplib.SMTPException as e:
        print(f"❌ Erreur SMTP : {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Si aucun argument, utiliser la dernière édition
        import yaml
        from build_newsletter import CONTENT_DIR
        
        issues = sorted(os.listdir(CONTENT_DIR))
        if not issues:
            print("❌ Aucune newsletter trouvée")
            sys.exit(1)
        issue = issues[-1]
        print(f"📰 Utilisation de la dernière édition : {issue}")
    else:
        issue = sys.argv[1]
    
    send_newsletter(issue)
