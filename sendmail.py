import smtplib
import os
from email.message import EmailMessage

def send_email(recipient, subject, body, sender=os.getenv("MAIL_SENDER"), password=os.getenv("MAIL_PASSWD"), smtp_server=os.getenv("MAIL_SERVER"), port=os.getenv("MAIL_PORT")):
    """
    Sendet eine E-Mail mit UTF-8-Kodierung und TLS-Verschlüsselung.
    """
    # Erstelle die E-Mail mit UTF-8
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_charset("utf-8")  # WICHTIG: UTF-8 setzen

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # TLS aktivieren
            server.login(sender, password)  # Anmeldung
            server.send_message(msg)  # Mail senden
        print("✅ E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"❌ Fehler beim Senden der E-Mail: {e}")


if __name__ == "__main__":
  # Beispielaufruf
  send_email(
    SENDER,
    os.getenv("MAIL_PASS"),
    recipient=os.getenv("MAIL_RECIPIENT"),
    subject="Test-Mail",
    body="Das ist ein Test mit Python!"
  )
