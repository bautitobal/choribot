import os
import requests
from datetime import datetime

def get_uptime(channel_name):
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": os.getenv('CLIENT_ID'),
        "Authorization": f"Bearer {os.getenv('BOT_TOKEN')}"
    }
    params = {"user_login": channel_name}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data["data"]:
            start_time = data["data"][0]["started_at"]
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
            uptime = datetime.utcnow() - start_time
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)} horas y {int(minutes)} minutos"
        return None
    except requests.RequestException as e:
        print("Error al obtener el uptime:", e)
        return None
