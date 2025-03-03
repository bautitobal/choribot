# Archivo que va a contener todos los timers del bot de twitch
# Programa empieza (basta de comentarios)
from twitchio.ext import commands
from utils.twitch_api import get_uptime
from twitchio.ext import commands
import asyncio

class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.social_channels = ["choribot11", "choripanycristi"]  # Cambia estos a los nombres de los canales donde quieres que se envíe el mensaje de redes sociales
        self.social_message = "¡Sígueme en mis redes sociales! Speedrun.com: https://speedrun.com/users/choripanycristi | Instagram: https://instagram.com/choripanycristi | X/Twitter: https://x.com/choripanycristi | TikTok: @choripanycristi."

        # Inicia las tareas
        self.bot.loop.create_task(self.social_timer())

    async def social_timer(self):
        await self.bot.wait_for_ready()
        while True:
            for channel_name in self.social_channels:
                channel = self.bot.get_channel(channel_name)
                if channel:
                    await channel.send(self.social_message)
            await asyncio.sleep(1800)  # Espera 30 minutos antes de enviar el mensaje nuevamente

def prepare(bot):
    bot.add_cog(Timers(bot))