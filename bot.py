from twitchio.ext import commands
from dotenv import load_dotenv
import os
from commands.general import GeneralCommands
from commands.openai_commands import OpenAICommands
from twitchio.ext.commands.errors import CommandNotFound
#from utils.env_utils import refresh_access_token_twitch_generator # Importar función para refrescar el token de Twitch
import re
#import datetime
from datetime import datetime
from utils.timers import Timers
from commands.general import prepare
from commands.personal_commands import PersonalCommands
from commands.mod import ModCommands
from utils.alerts import Alerts
from commands.deepseek_commands import DeepSeekCommands
from commands.openrouter_commands import OpenRouterCommands
from commands.translation_commands import TranslationCommands
from commands.commercial import CommercialCommands
import asyncio
from commands.quote import QuoteCommands
import logging
from twitchio import HTTPException
from twitchio.ext import commands

logging.basicConfig(filename='logs/bot_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN') # Es el token de acceso del bot (no el de la API de Twitch, el Bearer token o OAuth token)
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN') # Es el token de refresco del bot, llamado refresh_token
CHANNEL_NAMES = os.getenv("CHANNEL_NAMES").split(",") # Es una lista de los nombres de los canales a los que se conectará el bot
CLIENT_ID = os.getenv('CLIENT_ID')
BOT_NICK = os.getenv('BOT_NICK')

if not os.path.exists('logs'):
    os.makedirs('logs')
    print("Carpeta 'logs/' creada correctamente.")

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=BOT_TOKEN,
            client_id=CLIENT_ID,
            nick=BOT_NICK,
            prefix='!',
            initial_channels=CHANNEL_NAMES
        )
        #self.loop.create_task(self.send_periodic_messages())
        self.add_cog(GeneralCommands(self))
        self.add_cog(OpenAICommands(self))
        self.add_cog(PersonalCommands(self))
        self.add_cog(ModCommands(self))
        self.add_cog(DeepSeekCommands(self))
        self.add_cog(OpenRouterCommands(self))
        self.add_cog(TranslationCommands(self))
        self.add_cog(CommercialCommands(self))
        self.add_cog(QuoteCommands(self))
        self.load_commands()
    
        #asyncio.create_task(self.get_cog("CommercialCommands").start_commercial_timer())    

    async def event_ready(self):
        print(f'Bot listo | Logueado como: {self.nick}')
        
        # Filtrar canales válidos
        connected_channels = [channel for channel in self.connected_channels if channel is not None]
        failed_channels = list(set(CHANNEL_NAMES) - set([channel.name for channel in connected_channels]))

        print(f"Conectado a los canales: {', '.join([c.name for c in connected_channels]) if connected_channels else 'Ninguno'}")
        
        if failed_channels:
            print(f"[ERROR] No se pudo conectar a: {', '.join(failed_channels)}")
            logging.error(f"No se pudo conectar a: {', '.join(failed_channels)}")

        # Iniciar los timers solo con canales válidos
        if connected_channels:
            self.timers = Timers(self)
            self.timers.start_timers()
        
        commercial_cog = self.get_cog("CommercialCommands")
        if commercial_cog:
            asyncio.create_task(commercial_cog.start_commercial_timer())

    async def event_error(self, error: Exception):
        """Maneja los errores de TwitchIO, detectando si el bot fue baneado de un canal y registrándolo."""
        if isinstance(error, HTTPException) and error.status == 403:
            channel_name = None
            if hasattr(error, 'request') and error.request:
                match = re.search(r'channel_id=([^&]+)', str(error.request.url))
                if match:
                    channel_name = match.group(1)

            message = "[ERROR] El bot ha sido baneado"
            if channel_name:
                message += f" del canal {channel_name}"

            print(message)
            logging.error(message)
        else:
            logging.error(f"Error inesperado: {error}")
            print(f"[ERROR] {error}")
     
    # --- LOGS ---
    def load_commands(self):
        """Cargar comandos adicionales."""
        from commands.clips import ClipCommands
        self.add_cog(ClipCommands(self))
        print("Comandos adicionales cargados correctamente.")

    async def event_message(self, message):
        """Evento que se ejecuta cuando se recibe un mensaje en el chat."""
        if not message.echo:  # Ignorar mensajes del propio bot
            # Obtener la hora actual en formato YYYY-MM-DD HH:MM:SS
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Obtener el nombre del canal y el usuario
            channel_name = message.channel.name
            user_name = message.author.name
            content = message.content

            # Crear la línea de log
            log_line = f"{current_time} - from {channel_name} - [{user_name}] {content}\n"

            # Guardar el log en el archivo correspondiente
            self.save_log(log_line)

            # Procesar comandos
            await self.handle_commands(message)

    def save_log(self, log_line):
        """Guardar la línea de log en el archivo correspondiente."""
        # Obtener la fecha actual en formato YYYY-MM-DD
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Nombre del archivo de log
        log_file = f'logs/{current_date}.txt'

        # Guardar la línea de log en el archivo
        try:
            with open(log_file, 'a', encoding='utf-8') as file:
                file.write(log_line)
            print(f"Log guardado en: {log_file}")  # Depuración
        except Exception as e:
            print(f"Error al guardar el log: {e}")
    
    # --- ALERTAS ---
    async def event_follow(self, user):
        """Evento cuando un usuario sigue el canal."""
        print(f"Follow detectado: {user.name}")  # Depuración
        for channel_name in CHANNEL_NAMES:
            channel = self.get_channel(channel_name)
            if channel:
                await Alerts.on_follow(channel, user)

    async def event_subscription(self, user, tier, message):
        """Evento cuando un usuario se suscribe al canal."""
        print(f"Suscripción detectada: {user.name} (Tier {tier})")  # Depuración
        for channel_name in CHANNEL_NAMES:
            channel = self.get_channel(channel_name)
            if channel:
                await Alerts.on_subscription(channel, user, tier, message)

    async def event_resubscription(self, user, tier, months, message):
        """Evento cuando un usuario renueva su suscripción."""
        print(f"Resubscription detectada: {user.name} (Tier {tier}, {months} meses)")  # Depuración
        for channel_name in CHANNEL_NAMES:
            channel = self.get_channel(channel_name)
            if channel:
                await Alerts.on_resubscription(channel, user, tier, months, message)

    async def event_cheer(self, user, bits, message):
        """Evento cuando un usuario hace un cheer."""
        print(f"Cheer detectado: {user.name} ({bits} bits)")  # Depuración
        for channel_name in CHANNEL_NAMES:
            channel = self.get_channel(channel_name)
            if channel:
                await Alerts.on_cheer(channel, user, bits, message)

    async def event_raid(self, raider, viewers):
        """Evento cuando un canal hace un raid."""
        print(f"Raid detectado: {raider.name} con {viewers} espectadores")  # Depuración
        for channel_name in CHANNEL_NAMES:
            channel = self.get_channel(channel_name)
            if channel:
                await Alerts.on_raid(channel, raider, viewers)
       
    async def event_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            print(f"Comando no encontrado: {ctx.message.content}")
            return
        else:
            print(f"Error inesperado en el comando {ctx.message.content}: {error}")

    async def event_message(self, message):
        if message.echo or (message.author and message.author.name.lower() == self.nick.lower()):
            current_time = datetime.now().strftime("%H:%M")
            channel_name = message.channel.name
            print(f"{current_time} - from {channel_name} - [Bot] {message.content}")
            return

        # Si el mensaje no tiene autor (muy raro, pero por seguridad lo pongo)
        if message.author is None:
            print(f'Mensaje sin autor: "{message.content}"')
            return
        
        current_time = datetime.now().strftime("%H:%M")
        channel_name = message.channel.name
        user_name = message.author.name
        content = message.content
        bot = message.channel

        content_lower = content.lower()

        # Comandos de contexto saludo en inglés
        if re.search(r'\b(hi|hello|heya|hey|howdy|heyy|wass good|wassup|hellouda|hellothere)\b', content_lower): 
            await bot.send(f"Hi there! :D Welcome to the channel, {user_name}!")

        # Comandos de "eh"
        if content_lower in ("eh", "eh?", "ehh", "ehhh", "eee", "eheh", "ehhhh"):
            await bot.send("Tirame un eh más fuerte Kappa")

        if content_lower in ("que", "que?"):
            await bot.send("so. :tf:")

        # Comandos de contexto nombre (Ayden)
        if re.search(r'\b(aydenmk8|ayden|zarza(sr)?)\b', content_lower):
            await bot.send("Ayden")

        if re.search(r'\b(gl+|glgl|good ?luck|geel|bsbs)\b', content_lower):
            await bot.send(f"Thanks, {user_name}!")

        if re.search(r'\b(netflix|nflx|netfli|neeflix|nettflix|neflix)\b', content_lower):
            await bot.send(f"Te mentí, {user_name}, no tengo Netflix. ¡Encuerate! Kappa")

        if re.search(r'\b(hola|holla|holaa|holaaa|buenas|buendia|hoal|holi(wi)?s?|saluten)\b', content_lower):
            await bot.send(f"¡Hola, {user_name}! Bienvenido al canal.")

        if re.search(r'\b(chau|adios|bye|byebye|adiós|chao|chauu|adioss|adieu)\b', content_lower):
            await bot.send(f"¡Chau, {user_name}! ¡Gracias por pasar!")

        if "wutface" in content_lower:
            await bot.send("WutFace WutFace WutFace")

        # Comandos de :v
        if ":v" in content_lower:
            await bot.send("𝕕𝕠𝕤𝕡𝕦𝕟𝕥𝕠𝕤 𝕓𝕖 Kappa")

        # Comandos de rbrt27
        if re.search(r'\b(rbrt27|bobert|robert|robert27|bobert27)\b', content_lower):
            await bot.send("Imaginate llamarte rbrt27 Kappa")
        
        if re.search(r'\b(#nopechi)\b', content_lower):
            await bot.send("Comando !nopechi en el chat")
        
        # Comandos de why/por qué
        if re.search(r'\b(why|por\s*q(ué)?|por\s*que|why?)\b', content_lower):
            await bot.send("Because it's faster Kappa")

        # Comandos de RalpherZ
        if re.search(r'\b(ralpherz|ralph|rocco)\b', content_lower):
            await bot.send("RalpherZ es el perro de Chori de la LMS House RalpherZ")

        # Comandos de F
        if re.search(r'\b(f|ff|fff|efe)\b', content_lower):
            await bot.send("Press F to pay respects, chele")

        if re.search(r'\b(jab[oó]n(cito|ce?te)?|jaboon+)\b', content_lower):
            await bot.send("Hace como yo y usa jabón pa que resbale, pa. Te quiero vegano, saludos Kappa")

        if re.search(r'\b(choribot11|choribot111?)\b', content_lower):
            await bot.send("¡Ese soy yo! Kappa")

        # Comandos de GG
        if re.search(r'\b(gg(wp)?!?|gee ?gee|good ?game)\b', content_lower):
            await bot.send("GG WP!")

        # Comandos de PikuMatero
        if re.search(r'\b(pikumatero)\b', content_lower):
            await bot.send("PikuMatero")

        # Imprimir el mensaje en la consola
        print(f"{current_time} - from {channel_name} - [{user_name}] {content}")

        if not message.echo:
            await self.handle_commands(message)
        
if __name__ == '__main__':
    # Refrescar token antes de iniciar el bot
    #new_token = refresh_access_token_twitch_generator(REFRESH_TOKEN)
    #if new_token:
        #BOT_TOKEN = new_token

    bot = Bot()
    prepare(bot)
    bot.run()
