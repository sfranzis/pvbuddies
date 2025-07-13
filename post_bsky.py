from atproto import Client

USERNAME = os.getenv("BSKY_USER")
PASSWORD = os.getenv("BSKY_PASSWORD")

def post_to_bluesky(text):
    """Sendet einen Post an Bluesky."""
    client = Client()
    client.login(USERNAME, PASSWORD)
    client.send_post(text=text)
    print("✅ Post erfolgreich auf BlueSky veröffentlicht!")
