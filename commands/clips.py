import os
import requests
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv()

BOT_NICK = os.getenv('BOT_NICK')
CLIENT_ID = os.getenv('CLIENT_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

class ClipCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_broadcaster_id(self, channel_name):
        """
        Obtiene el ID del broadcaster (canal) usando el nombre del canal.
        """
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {BOT_TOKEN}',
        }
        url = f'https://api.twitch.tv/helix/users?login={channel_name}'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["id"]
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el broadcaster ID: {e}")
            return None

    @commands.command(name='clip')
    async def create_clip(self, ctx):
        """
        Comando !clip: Crea un clip en el canal actual.
        """
        channel_name = ctx.channel.name if hasattr(ctx.channel, 'name') else ctx.channel
        broadcaster_id = await self.get_broadcaster_id(channel_name)
        if not broadcaster_id:
            await ctx.send("No se pudo obtener el ID del canal.")
            return

        # Verificar si el usuario tiene permisos para crear un clip
        user_is_mod = await self.is_mod(broadcaster_id, ctx.author.id)
        if not (ctx.author.name.lower() == channel_name.lower() or user_is_mod):
            await ctx.send("Solo el streamer o moderadores pueden crear clips.")
            return

        # Crear el clip usando la API de Twitch
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {BOT_TOKEN}',
        }
        url = f'https://api.twitch.tv/helix/clips?broadcaster_id={broadcaster_id}'
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            clip_id = data["data"][0]["id"]
            clip_url = f"https://clips.twitch.tv/{clip_id}"
            await ctx.send(f"¡Clip creado! Puedes verlo aquí: {clip_url}")
        except requests.exceptions.RequestException as e:
            print(f"Error al crear el clip: {e}")
            await ctx.send(f"Hubo un error al crear el clip. Inténtalo de nuevo más tarde: {e}")

    async def is_mod(self, broadcaster_id, user_id):
        """
        Verifica si un usuario es moderador en el canal.
        """
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {BOT_TOKEN}',
        }
        url = f'https://api.twitch.tv/helix/moderation/moderators?broadcaster_id={broadcaster_id}&user_id={user_id}'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return len(data["data"]) > 0
        except requests.exceptions.RequestException as e:
            print(f"Error al verificar moderador: {e}")
            return False

# Configurar el cog
def prepare(bot):
    bot.add_cog(ClipCommands(bot))