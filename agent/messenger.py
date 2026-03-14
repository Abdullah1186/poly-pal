import os
import requests


def send_whatsapp(to: str, body: str):
    """Send a WhatsApp message via Meta Cloud API.
    `to` should be a plain number e.g. '447739863789' (no + or whatsapp: prefix).
    """
    phone_number_id = os.environ["META_PHONE_NUMBER_ID"]
    access_token = os.environ["META_ACCESS_TOKEN"]

    response = requests.post(
        f"https://graph.facebook.com/v19.0/{phone_number_id}/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        },
    )
    print(f"Meta API response {response.status_code}: {response.text}")
    response.raise_for_status()
