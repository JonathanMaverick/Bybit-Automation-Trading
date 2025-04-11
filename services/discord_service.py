import requests
import io
from PIL import Image
from config import DISCORD_WEBHOOK

def send_discord(message: str):
    if not DISCORD_WEBHOOK:
        print("Discord Webhook not configured.")
        return

    payload = {
        "content": message
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")


def send_discord_image(message: str, image: Image.Image):
    if not DISCORD_WEBHOOK:
        print("Discord Webhook not configured.")
        return

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)

    files = {
        'file': ('chart.png', buffered, 'image/png')
    }

    payload = {
        "content": message
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, data=payload, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord image: {e}")