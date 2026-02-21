import os
import sys
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Charger .env localement si disponible (dev mode)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv non disponible (normal sur GitHub Actions)
    pass

# Variables d'environnement (via .env local ou GitHub Secrets)
SENDER_EMAIL = os.getenv("NEWSLETTER_EMAIL")
SENDER_PASSWORD = os.getenv("NEWSLETTER_PASSWORD")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_RANGE = os.getenv("GOOGLE_SHEET_RANGE", "Sheet1!A2:A")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
DIST_DIR = "dist"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_google_credentials():
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    if GOOGLE_SERVICE_ACCOUNT_FILE:
        return Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    print("❌ Erreur : Identifiants Google Sheets manquants")
    print("   Définis GOOGLE_SERVICE_ACCOUNT_JSON ou GOOGLE_SERVICE_ACCOUNT_FILE")
    sys.exit(1)


def load_recipients_from_sheet():
    if not GOOGLE_SHEET_ID:
        print("❌ Erreur : GOOGLE_SHEET_ID manquant")
        sys.exit(1)

    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=GOOGLE_SHEET_RANGE,
    ).execute()
    values = result.get("values", [])

    emails = []
    for row in values:
        for cell in row:
            cell = (cell or "").strip()
            if cell and "@" in cell:
                emails.append(cell)

    emails = list(dict.fromkeys(emails))
    if not emails:
        print("❌ Erreur : Aucun destinataire trouvé dans Google Sheets")
        sys.exit(1)

    return emails


def send_newsletter(issue):
    """Envoie la newsletter HTML par email."""
    
    # Vérifier que les paramètres sont configurés
    if not all([SENDER_EMAIL, SENDER_PASSWORD]):
        print("❌ Erreur : Variables d'environnement manquantes")
        print("   Assurez-vous que NEWSLETTER_EMAIL, NEWSLETTER_PASSWORD sont définis")
        print("   - Localement : via .env")
        print("   - GitHub Actions : via Secrets")
        sys.exit(1)
    
    # Charger le fichier HTML
    html_path = os.path.join(DIST_DIR, f"{issue}.html")
    if not os.path.exists(html_path):
        print(f"❌ Erreur : Fichier HTML non trouvé : {html_path}")
        sys.exit(1)
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extraire le titre de la newsletter du HTML
    match = re.search(r'<title>(.*?)</title>', html_content)
    subject = match.group(1) if match else f"Newsletter {issue}"
    
    # Préparer l'email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    # Utiliser BCC pour masquer les destinataires entre eux
    # Le champ "To" reste vide ou contient l'expéditeur pour éviter les spams
    message["To"] = SENDER_EMAIL  # Évite que l'email soit marqué comme spam
    
    # Charger les destinataires depuis Google Sheets
    recipients = load_recipients_from_sheet()
    
    # Ajouter le contenu HTML
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    # Envoyer l'email
    try:
        print(f"📧 Connexion à {SMTP_SERVER}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            # sendmail() prend la liste réelle des destinataires
            server.sendmail(SENDER_EMAIL, recipients, message.as_string())
        
        print(f"✅ Newsletter envoyée avec succès à {len(recipients)} destinataire(s) en BCC")
        print(f"   Sujet : {subject}")
    
    except smtplib.SMTPAuthenticationError:
        print("❌ Erreur d'authentification : Vérifiez vos identifiants Gmail")
        print("   💡 Utilisez un 'App Password' si vous avez 2FA activé")
        print("   📖 https://myaccount.google.com/apppasswords")
        sys.exit(1)
    
    except smtplib.SMTPException as e:
        print(f"❌ Erreur SMTP : {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Récupérer l'issue depuis l'argument ou l'env (GitHub Actions)
    issue = None
    
    if len(sys.argv) > 1 and sys.argv[1].strip():
        issue = sys.argv[1]
        print(f"📰 Sending issue from argument: {issue}")
    elif os.getenv("NEWSLETTER_ISSUE"):
        issue = os.getenv("NEWSLETTER_ISSUE")
        print(f"📰 Sending issue from env: {issue}")
    else:
        # Utiliser la dernière édition (dossier 'content')
        # build_newsletter n'exporte plus CONTENT_DIR — on utilise 'content' par défaut.
        content_dir = "content"
        if not os.path.isdir(content_dir):
            print(f"❌ Erreur : Dossier de contenu introuvable : {content_dir}")
            sys.exit(1)

        issues = sorted(os.listdir(content_dir))
        if not issues:
            print(f"❌ Aucune newsletter trouvée dans {content_dir}")
            sys.exit(1)
        issue = issues[-1]
        print(f"📰 Sending latest issue: {issue}")
    
    send_newsletter(issue)

