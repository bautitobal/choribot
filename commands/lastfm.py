import aiohttp
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Cargar el archivo JSON con los nombres de usuario de Last.fm
def load_lastfm_channels():
    with open("lastfm-channels.json", "r") as file:
        return json.load(file)

async def get_current_song(username):
    """Obtiene la canción actual de Last.fm según el nombre de usuario."""
    api_key = os.getenv("LASTFM_API_KEY")   
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&format=json&limit=1"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                if "recenttracks" in data and "track" in data["recenttracks"]:
                    track = data["recenttracks"]["track"][0]
                    song = track["name"]
                    artist = track["artist"]["#text"]
                    return f"🎵 {song} - {artist}"
                else:
                    return "No hay ninguna canción en reproducción en este momento."
    except Exception as e:
        print(f"Error al obtener la canción de Last.fm: {e}")
        return "Error al obtener la canción."