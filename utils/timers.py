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
            for channel_name in self.bot.connected_channels:
                if await self._is_channel_live(channel_name):
                    await self._send_message_to_channel(channel_name, "Gracias por estar en este tu stream :D")
            await asyncio.sleep(1500)  # Cada 25 minutos

    async def _send_reminder_message(self):
        await self.bot.wait_for_ready()
        while True:
            for channel_name in self.bot.connected_channels:
                if await self._is_channel_live(channel_name):
                    await self._send_message_to_channel(channel_name, "No olvides de usar el comando !choribot para hacer tus preguntas!")
            await asyncio.sleep(3600)  # Cada 60 minutos

    async def _send_message_to_channel(self, channel_name, message):
        try:
            if isinstance(channel_name, str):
                channel = self.bot.get_channel(channel_name.strip().lower())
            elif hasattr(channel_name, "name"):
                channel = channel_name
            else:
                print(f"Tipo de canal no soportado: {type(channel_name)}")
                return

            if channel:
                await channel.send(message)
                #print(f"Mensaje enviado a {channel.name}: {message}")
            else:
                print(f"No se pudo obtener el canal: {channel_name}")
        except Exception as e:
            print(f"Error al enviar mensaje a {channel_name}: {e}")

    async def _is_channel_live(self, channel_name):
        """Verifica si el canal está en vivo usando la API de Twitch."""
        try:
            if isinstance(channel_name, str):
                channel_name = channel_name.strip().lower()
            elif hasattr(channel_name, "name"):
                channel_name = channel_name.name.lower()
            else:
                print(f"Tipo de canal no soportado para verificar estado en vivo: {type(channel_name)}")
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

            #print(f"Respuesta de la API de Twitch para {channel_name}: {data}") # Depuración de la respuesta de la API
            # Si hay datos en 'data', el canal está en vivo
            if data.get("data"):
                stream_info = data["data"][0]
                game_name = stream_info.get("game_name", "Juego desconocido")
                viewer_count = stream_info.get("viewer_count", 0)
                title = stream_info.get("title", "Sin título")
                print(f'{channel_name} está en vivo jugando a {game_name} con {viewer_count} espectadores: "{title}"')
                return stream_info
            #print(f'{channel_name} no está en vivo.')
            return None
            # Si hay datos en 'data', el canal está en vivo
            #if data.get("data"):
                #return True
            #return False
        except Exception as e:
            print(f"Error al verificar si el canal {channel_name} está en vivo: {e}")
            return None
