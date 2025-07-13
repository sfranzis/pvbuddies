import os
from mastodon import Mastodon

# Zugangsdaten
ACCESS_TOKEN = os.getenv("MASTODON_API_TOKEN")
API_BASE_URL = os.getenv("MASTODON_INSTANCE")

# Mastodon-Client initialisieren
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=API_BASE_URL
)

def post_to_mastodon(message):
    try:
        response = mastodon.status_post(message, visibility="public")
        print("✅ Post erfolgreich gesendet!")
    except Exception as e:
        print(f"❌ Fehler beim Posten: {e}")

