import asyncio
import aiohttp

class Timers:
    def __init__(self, bot):
        self.bot = bot

    def start_timers(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._send_thank_you_message())
        loop.create_task(self._send_reminder_message())

    async def _send_thank_you_message(self):
        await self.bot.wait_for_ready()
        while True:
            for channel in self._get_valid_channels():
                if await self._is_channel_live(channel):
                    await self._send_message_to_channel(channel, "Gracias por estar en este tu stream :D")
            await asyncio.sleep(1500)  # Cada 25 minutos

    async def _send_reminder_message(self):
        await self.bot.wait_for_ready()
        while True:
            for channel in self._get_valid_channels():
                if await self._is_channel_live(channel):
                    await self._send_message_to_channel(channel, "No olvides de usar el comando !choribot para hacer tus preguntas!")
            await asyncio.sleep(3600)  # Cada 60 minutos

    def _get_valid_channels(self):
        """Filtra y devuelve solo los canales válidos en los que el bot está conectado."""
        return [channel for channel in self.bot.connected_channels if channel is not None]

    async def _send_message_to_channel(self, channel, message):
        """Envía un mensaje a un canal específico si es válido."""
        try:
            if isinstance(channel, str):
                channel = self.bot.get_channel(channel.strip().lower())
            
            if channel is None:
                print(f"[ERROR] No se pudo obtener el canal: {channel}")
                return

            await channel.send(message)
            #print(f"Mensaje enviado a {channel.name}: {message}") # Es solo para depuración
        except Exception as e:
            print(f"Error al enviar mensaje a {channel}: {e}")

    async def _is_channel_live(self, channel):
        """Verifica si el canal está en vivo usando la API de Twitch."""
        try:
            channel_name = channel.strip().lower() if isinstance(channel, str) else channel.name.lower() if hasattr(channel, "name") else None
            
            if not channel_name:
                print(f"[ERROR] Tipo de canal no soportado para verificar estado en vivo: {type(channel)}")
                return None

            # Endpoint de Twitch para verificar transmisiones
            url = f"https://api.twitch.tv/helix/streams?user_login={channel_name}"

            headers = {
                "Client-ID": "gp762nuuoqcoxypju8c569th9wz7q5",
                "Authorization": "Bearer ewdh7n58qj5z72sdxzxe4hvikkd2cd"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()

            if data.get("data"):
                stream_info = data["data"][0]
                game_name = stream_info.get("game_name", "Juego desconocido")
                viewer_count = stream_info.get("viewer_count", 0)
                title = stream_info.get("title", "Sin título")
                print(f'{channel_name} está en vivo jugando a {game_name} con {viewer_count} espectadores: "{title}"')
                return stream_info
            
            return None
        except Exception as e:
            print(f"Error al verificar si el canal {channel} está en vivo: {e}")
            return None
