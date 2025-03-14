from twitchio.ext import commands
from dotenv import load_dotenv
import os
from commands.general import GeneralCommands
from commands.openai_commands import OpenAICommands
from twitchio.ext.commands.errors import CommandNotFound
#from utils.env_utils import refresh_access_token_twitch_generator # Importar función para refrescar el token de Twitch
import re
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
from server import start_server
from commands.dolar_api import DolarCommands
from commands.cotizaciones_api import CotizacionesCommands

logging.basicConfig(filename='logs/bot_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
#start_server()

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
        self.start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        os.makedirs("logs", exist_ok=True)
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
        self.add_cog(DolarCommands(self))
        self.add_cog(CotizacionesCommands(self))
        self.load_commands()
    
        #asyncio.create_task(self.get_cog("CommercialCommands").start_commercial_timer())    

    async def event_ready(self):
        print(f'Bot listo | Logueado como: {self.nick}')
        
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
     
    def load_commands(self):
        """Cargar comandos adicionales."""
        from commands.clips import ClipCommands
        self.add_cog(ClipCommands(self))
        print("Comandos adicionales cargados correctamente.")
        
    # --- LOGS ---
    async def event_message(self, message):
        """Evento que se ejecuta cuando se recibe un mensaje en el chat."""

        current_time = datetime.now().strftime("%H:%M")
        full_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        channel_name = message.channel.name if message.channel else "Unknown"

        # **Si el mensaje es del bot, mostrarlo en consola y log**
        if message.echo or (message.author and message.author.name.lower() == self.nick.lower()):
            print(f"{current_time} - from {channel_name} - [Bot] {message.content}") # Depuración
            self.save_log(f"{full_time} - from {channel_name} - [Bot] {message.content}\n")
            return
        
        if message.author is None:
            print(f'Mensaje sin autor: "{message.content}"')
            return

        user_name = message.author.name
        content = message.content
        content_lower = content.lower()

        print(f"{current_time} - from {channel_name} - [{user_name}] {content}") # Depuración
        self.save_log(f"{full_time} - from {channel_name} - [{user_name}] {content}\n")

        if content.startswith("!"):
            response = await self.handle_commands(message)  # Se ejecuta el comando y obtiene la respuesta
            if response:
                await message.channel.send(response)
                print(f"{current_time} - from {channel_name} - [Bot] {response}") # Depuración
                self.save_log(f"{full_time} - from {channel_name} - [Bot] {response}\n")

        # **Comandos de contexto (regex)**
        response = None

        if re.search(r'\b(hi|hello|heya|hey|howdy|wassup|hellouda|hellothere|wass good|heyy|helloo)\b', content_lower):
            response = f"Hi there! :D Welcome to the channel, {user_name}!"
        elif content_lower in ("eh", "eh?", "ehh", "ehhh", "eee", "eheh"):
            response = "Tirame un eh más fuerte Kappa"
        elif content_lower in ("que", "que?"):
            response = "so. :tf:"
        elif re.search(r'\b(aydenmk8|ayden|zarza(sr)?)\b', content_lower):
            response = "Ayden"
        elif re.search(r'\b(gl+|glgl|good ?luck|geel|bsbs)\b', content_lower):
            response = f"Thanks, {user_name}!"
        elif re.search(r'\b(netflix|nflx|netfli|neeflix|nettflix|neflix)\b', content_lower):
            response = f"Te mentí, {user_name}, no tengo Netflix. ¡Encuerate! Kappa"
        elif re.search(r'\b(hola|holla|holaa|holaaa|buenas|buendia|hoal|holi(wi)?s?|saluten)\b', content_lower):
            response = f"¡Hola, {user_name}! Bienvenido al canal."
        elif re.search(r'\b(chau|adios|bye|byebye|adiós|chao|chauu|adioss|adieu)\b', content_lower):
            response = f"¡Chau, {user_name}! ¡Gracias por pasar!"
        elif "wutface" in content_lower:
            response = "WutFace WutFace WutFace"
        elif ":v" in content_lower:
            response = "𝕕𝕠𝕤𝕡𝕦𝕟𝕥𝕠𝕤 𝕓𝕖 Kappa"
        elif re.search(r'\b(rbrt27|bobert|robert|robert27|bobert27)\b', content_lower):
            response = "Imaginate llamarte rbrt27 Kappa"
        elif re.search(r'\b(#nopechi|nopechi|NOPECHI|nopechis|nopechhi|no ?pechi|no ?pechi ?eh|pechear|no ?la ?pechees|pechees)\b', content_lower):
            response = "#NOPECHI comando !nopechi en el chat 🙏"
        elif content_lower in ("why", "por qué", "por que", "why?", "por qué?", "whyy", "por"):
            response = "Because it's faster Kappa"
        elif re.search(r'\b(ralpherz|ralph|rocco)\b', content_lower):
            response ="RalpherZ es el perro de Chori de la LMS House RalpherZ"
        elif re.search(r'\b(jab[oó]n(cito|ce?te)?|jaboon+)\b', content_lower):
            response = "Hace como yo y usa jabón pa que resbale, pa. Te quiero vegano, saludos Kappa"
        elif re.search(r'\b(choribot11|choribot111?)\b', content_lower):
            response = "¡Ese soy yo! Kappa"
        elif re.search(r'\b(gg(wp)?!?|gee ?gee|good ?game|bien ?jugado|bien ?jugado ?gg|gg)\b', content_lower):
            response = "GG WP!"
        elif re.search(r'\b(pikumatero|PikuMatero|pikuniku|piku)\b', content_lower):
            response = "PikuMatero"
        elif re.search(r'\b(lmao|lol|rofl|limao|lul|LUL|jajaja|jaja|xD|loll|haha|hahaha|xdd|gracioso|funny|risa)\b', content_lower):
            response = "LMAO 😂"
        elif re.search(r'\b(rip|RIP|f|ff|F|rips|qepd|muerto|dead)\b', content_lower):
            response = "Press F to pay respects, chele"

        if response:
            await message.channel.send(response)

    def save_log(self, log_line):
        """Guardar la línea de log en el archivo correspondiente."""
        log_file = f'logs/{self.start_time}.txt'  

        try:
            with open(log_file, 'a', encoding='utf-8') as file:
                file.write(log_line)
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
            
if __name__ == '__main__':
    # Refrescar token antes de iniciar el bot
    #new_token = refresh_access_token_twitch_generator(REFRESH_TOKEN)
    #if new_token:
        #BOT_TOKEN = new_token

    bot = Bot()
    prepare(bot)
    bot.run()
