from twitchio.ext import commands
import asyncio
import os
from datetime import datetime
import aiohttp

class CommercialCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commercial_interval = int(os.getenv("COMMERCIAL_INTERVAL", 1800))
        self.commercial_length = int(os.getenv("COMMERCIAL_LENGTH", 60))  
        self.is_running = True  # True por defecto
        self.client_id = os.getenv("CLIENT_ID")  # Client ID de Twitch
        self.oauth_token = os.getenv("BOT_TOKEN")  # OAuth Token del bot

    async def is_channel_live(self, channel_name):
        """
        Verifica si un canal está en vivo usando la API de Helix.
        """
        url = f"https://api.twitch.tv/helix/streams?user_login={channel_name}"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.oauth_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return bool(data["data"])  # Si hay datos, el canal está en vivo
                else:
                    print(f"Error al verificar el estado del canal {channel_name}: {response.status}")
                    return False

    async def start_commercial_timer(self):
        """
        Inicia el timer de publicidad automática.
        """
        if self.is_running:
            return 

        self.is_running = True
        while self.is_running:
            await asyncio.sleep(self.commercial_interval)

            # Ejecutar el comando /commercial en los canales conectados que estén en vivo
            for channel in self.bot.connected_channels:
                channel_name = channel.name
                if await self.is_channel_live(channel_name):
                    #print(f"[{datetime.now().strftime('%H:%M:%S')}] Ejecutando comercial en {channel_name} por {self.commercial_length} segundos.")
                    
                    await channel.send(f"/commercial {self.commercial_length}")

                    # Mostrar un console log después de ejecutar el comercial
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Comercial ejecutado en {channel_name} por {self.commercial_length} segundos.")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] El canal {channel_name} no está en vivo. No se ejecutará el comercial.")
                    print()

    async def stop_commercial_timer(self):
        """
        Detiene el timer de publicidad automática.
        """
        self.is_running = False

    @commands.command(name='startcommercial')
    async def start_commercial(self, ctx):
        """
        Comando !startcommercial: Inicia el timer de publicidad automática.
        """
        if self.is_running:
            await ctx.send("El timer de publicidad ya está en ejecución.")
            return

        await ctx.send("Iniciando el timer de publicidad automática...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer de publicidad iniciado por {ctx.author.name}.")
        await self.start_commercial_timer()

    @commands.command(name='stopcommercial')
    async def stop_commercial(self, ctx):
        """
        Comando !stopcommercial: Detiene el timer de publicidad automática.
        """
        if not self.is_running:
            await ctx.send("El timer de publicidad no está en ejecución.")
            return

        await ctx.send("Deteniendo el timer de publicidad automática...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer de publicidad detenido por {ctx.author.name}.")
        await self.stop_commercial_timer()