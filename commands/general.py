from twitchio.ext import commands
from utils.twitch_api import get_uptime
import requests
import os
import random
from dotenv import load_dotenv
import json
from commands.lastfm import get_current_song, load_lastfm_channels
from .speedrun import get_world_record, get_personal_bests
import time
import asyncio
from .cooldown import CooldownManager
from utils.cooldown_messages import cooldown_messages
from utils.specs_random import procesadores, gpus, rams, almacenamiento, sistema_operativo
from utils.random_quotes import frases
from utils.paya_quotes import paya_comments
load_dotenv()

# Configuración del bot
BOT_NICK = os.getenv('BOT_NICK')
CLIENT_ID = os.getenv('CLIENT_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_NAMES = os.getenv('CHANNEL_NAMES', '').split(',')


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counters_file = "counters.json"  # Archivo para guardar contadores
        self.lastfm_channels = load_lastfm_channels()  # Cargar los nombres de usuario de Last.fm
        self.cooldown_manager = CooldownManager()
        self.donation_links = self.load_donation_links()
        # Cargo
        with open("commands.json", "r", encoding="utf-8") as file:
            self.commands_data = json.load(file)
            
    
    def save_counters(self, data):
        """Guarda los contadores en el archivo JSON."""
        with open(self.counters_file, "w") as file:
            json.dump(data, file)

    def load_counters(self):
        """Carga los contadores desde el archivo JSON."""
        try:
            with open(self.counters_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        
    def load_donation_links(self):
        """Cargar los enlaces de donación desde el archivo JSON."""
        try:
            with open('donations.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Error: El archivo 'donations.json' no existe.")
            return {}
        except json.JSONDecodeError:
            print("Error: El archivo 'donations.json' tiene un formato inválido.")
            return {}
        
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
        
    # Comandos
    @commands.command(name="comandos")
    
    async def comandos(self, ctx: commands.Context):
        """Muestra la lista de comandos globales disponibles."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "comandos", cooldown_time)
        
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        global_commands = self.commands_data["globales"]
        # Lista de nombres de comandos globales
        global_command_names = [cmd["nombre"] for cmd in global_commands]
        # Mostrar la lista de comandos globales
        command_list = f"@{ctx.author.name} -> " + ", ".join(global_command_names)
        await ctx.send(
            f"{command_list}.\n\n "
            "Para obtener más información sobre un comando, escribe: \n"
            "!help <comando> (descripción en español) \n"
            "!help-en <comando> (descripción en inglés)"
        )

    @commands.command(name="commands")
    async def commands_en(self, ctx: commands.Context):
        """Shows the list of available global commands in English."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "commands", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        global_commands = self.commands_data["globales"]
        # List of global command names
        global_command_names = [cmd["nombre"] for cmd in global_commands]
        # Show the command list
        command_list = f"@{ctx.author.name} -> " + ", ".join(global_command_names)
        await ctx.send(
            f"{command_list}\n\n "
            "For more information about a command, type: \n"
            "!help <command> (description in Spanish) \n"
            "!help-en <command> (description in English)"
        )

    @commands.command(name="help")
    async def help(self, ctx: commands.Context):
        """Muestra la descripción en español de un comando."""
        cooldown_time = 20
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "help", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        args = ctx.message.content.split()
        if len(args) < 2:
            await ctx.send("Uso correcto: !help <nombre-comando>")
            return
        
        command_name = args[1].lower()
        command_found = False
        # Buscar el comando en la lista de comandos globales
        for cmd in self.commands_data["globales"]:
            if cmd["nombre"].lower() == command_name:
                await ctx.send(f"{cmd['nombre']}: {cmd['descripcion']}")
                command_found = True
                break

        # Buscar el comando en la lista de comandos personales (si el canal es choripanycristi o choribot11)
        if not command_found and ctx.channel.name.lower() in ["choripanycristi", "choribot11"]:
            for cmd in self.commands_data["personales"]:
                if cmd["nombre"].lower() == command_name:
                    await ctx.send(f"{cmd['nombre']}: {cmd['descripcion']}")
                    command_found = True
                    break
        if not command_found:
            await ctx.send(f"No se encontró el comando: {command_name}")

    @commands.command(name="help-en")
    async def help_en(self, ctx: commands.Context):
        """Muestra la descripción en inglés de un comando."""
        cooldown_time = 20
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "help-en", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        args = ctx.message.content.split()
        if len(args) < 2:
            await ctx.send("Incorrect usage: !help-en <command-name>")
            return

        command_name = args[1].lower()
        command_found = False
        # Buscar el comando en la lista de comandos globales
        for cmd in self.commands_data["globales"]:
            if cmd["nombre"].lower() == command_name:
                await ctx.send(f"{cmd['nombre']}: {cmd['description']}")
                command_found = True
                break

        # Buscar el comando en la lista de comandos personales (si el canal es choripanycristi o choribot11)
        if not command_found and ctx.channel.name.lower() in ["choripanycristi", "choribot11"]:
            for cmd in self.commands_data["personales"]:
                if cmd["nombre"].lower() == command_name:
                    await ctx.send(f"{cmd['nombre']}: {cmd['description']}")
                    command_found = True
                    break
        if not command_found:
            await ctx.send(f"Command not found: {command_name}")
    
    @commands.command(name="wr")
    async def wr(self, ctx: commands.Context):
        """Comando !wr para obtener el récord mundial de un juego."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "wr", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        args = ctx.message.content.split()
        if len(args) < 2:
            await ctx.send("Uso correcto: !wr <nombre del juego> [categoría]")
            return

        game_name = " ".join(args[1:-1]) if len(args) > 2 else args[1]
        category = args[-1] if len(args) > 2 else None
        wr_data = await get_world_record(game_name, category)
        if wr_data:
            await ctx.send(
                f"🎮 Juego: {wr_data['game']}\n"
                f"🏆 Categoría: {wr_data['category']}\n"
                f"⏱️ WR: {wr_data['time']}\n"
                f"🏃‍♂️ Runner: {wr_data['runner']}"
            )
        else:
            await ctx.send("No se encontró el récord mundial para el juego o categoría especificados.")

    @commands.command(name="pb")
    async def pb(self, ctx: commands.Context):
        """Comando !pb para mostrar los PBs del streamer o de un usuario específico."""
        cooldown_time = 20
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "pb", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        args = ctx.message.content.split()
        if len(args) < 2:
            # Si no se proporciona un usuario, usar el nombre del streamer
            username = ctx.channel.name  # Nombre del canal (streamer)
        else:
            username = args[1]  # Usuario proporcionado por el comando

        pbs = await get_personal_bests(username)
        if pbs:
            pb_messages = [f"🎮 {pb['game']} ({pb['category']}): ⏱️ {pb['time']}" for pb in pbs]
            await ctx.send(f"PBs de {username}:\n" + "\n".join(pb_messages))
        else:
            await ctx.send(f"No se encontraron PBs para {username}.")
    
    @commands.command(name="moto")
    async def moto(self, ctx):
        """Comando !moto para contar las motos."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "moto", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        counters = self.load_counters()  # Carga los contadores
        if "moto" not in counters:
            counters["moto"] = 0
        counters["moto"] += 1
        self.save_counters(counters)  # Guarda el contador actualizado
        await ctx.channel.send(f"Se han guardado {counters['moto']} motos 🚲! cacandrea%")

    @commands.command(name="choripan")
    async def choripan(self, ctx):
        """Comando !choripan para contar choripanes."""
        cooldown_time = 15
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "choripan", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        counters = self.load_counters()
        if "choripan" not in counters:
            counters["choripan"] = 0
        counters["choripan"] += 1
        self.save_counters(counters)  # Guarda el contador actualizado
        await ctx.channel.send(f"Se han compartido {counters['choripan']} choripanes 🌭! A choribot11 le gusta eso, muchas gracias {ctx.author.name}.")
    
    @commands.command(name="crab")
    async def crab(self, ctx):
        """Comando !crab con 50% de probabilidad de éxito."""
        cooldown_time = 7
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "crab", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        counters = self.load_counters()  
        if "crabs" not in counters:
            counters["crabs"] = 0

        if random.random() < 0.5:  # Probabilidad del 50%
            counters["crabs"] = 0  # Reinicia el contador
            self.save_counters(counters)  # Guarda el cambio
            await ctx.channel.send(f"{ctx.author.name} no consiguió cangrejos 🦀. ¡Prueba otra vez!")
        else:
            counters["crabs"] += 1
            self.save_counters(counters)  # Guarda el contador actualizado
            await ctx.channel.send(f"🦀 {ctx.author.name} ha encontrado un cangrejo! Total: {counters['crabs']} cangrejos.")
    
    @commands.command(name='7tv')
    async def sietetv(self, ctx):
        cooldown_time = 60
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "7tv", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        await ctx.channel.send("Use 7TV for extra emotes it's pretty cool and stuff")

    @commands.command(name="paya")
    async def paya(self, ctx: commands.Context):
        """Comando !paya para enviar un comentario random de elpayasitogamer."""
        cooldown_time = 15
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "paya", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        # Seleccionar un comentario aleatorio
        random_comment = random.choice(paya_comments)
        await ctx.send(random_comment)
        
    @commands.command(name="so")
    async def shoutout(self, ctx, channel: str = None):
        """Da un shoutout a un streamer específico. Solo para moderadores."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "so", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        # Verificar si el autor es moderador
        if not ctx.author.is_mod:
            await ctx.channel.send(f"{ctx.author.name}, no tienes permiso para usar este comando. 🚫")
            return
        # Verificar si se proporcionó el nombre del canal
        if not channel:
            await ctx.channel.send("Por favor, especifica el nombre de un canal. Ejemplo: !so streamer_name")
            return
        # Enviar el mensaje de shoutout
        await ctx.channel.send(f"¡No olviden pasarse por el canal de @{channel}! 💜 {channel} es un streamer genial, ¡denle amor y apoyo! (respeto máximo) https://twitch.tv/{channel.lower()}")
    
    # Comando borrar
    @commands.command(name='borrar')
    async def borrar(self, ctx):
        cooldown_time = 10
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "borrar", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        await ctx.channel.send("Borralo a la mierda chee Kappa")

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Comando !ping para medir el tiempo de respuesta del bot."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "ping", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        start_time = time.time()
        await ctx.send(f"@{ctx.author.name}, calculando ping...")
        await asyncio.sleep(0.1)
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        await ctx.send(f"@{ctx.author.name}, el tiempo de respuesta del bot es de {latency} ms.")

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        cooldown_time = 60
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "uptime", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        uptime = get_uptime(ctx.channel.name)
        if uptime:
            await ctx.channel.send(f"El stream lleva activo por {uptime}.")
        else:
            await ctx.channel.send("El stream no está activo en este momento.")
    
    # Comando !winner para elegir un ganador aleatorio
    @commands.command(name='winner')
    async def winner(self, ctx):
        cooldown_time = 60
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "winner", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        # Verifica si el autor es un moderador o el streamer
        user_is_mod = ctx.author.is_mod
        user_is_streamer = ctx.author.name.lower() == BOT_NICK.lower()

        if user_is_mod or user_is_streamer:
            # Obtener los espectadores activos
            url = f"https://tmi.twitch.tv/group/user/{ctx.channel.name}/chatters"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                viewers = data["chatters"]["viewers"]
                moderators = data["chatters"]["moderators"]
                all_users = viewers + moderators

                # Elegir un ganador aleatorio
                winner = random.choice(all_users)
                await ctx.channel.send(f"¡El ganador es: {winner}!")
            except requests.RequestException as e:
                print("Error al obtener los espectadores:", e)
                await ctx.channel.send("No pude obtener los espectadores. Intenta más tarde.")
        else:
            await ctx.channel.send("Solo los moderadores o el streamer pueden elegir un ganador.")
    
    # Comando !game
    @commands.command(name='game')
    async def game(self, ctx):
        cooldown_time = 20
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "game", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        # Verifica si el autor es un moderador o el streamer
        user_is_mod = ctx.author.is_mod
        user_is_streamer = ctx.author.name.lower() == BOT_NICK.lower()

        if ctx.message.content.strip().lower() == "!game":
            url = f"https://api.twitch.tv/helix/streams"
            headers = {
                "Client-ID": CLIENT_ID,
                "Authorization": f"Bearer {BOT_TOKEN}"
            }
            params = {
                "user_login": ctx.channel.name
            }

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if data["data"]:
                    game_name = data["data"][0].get("game_name", "Desconocido")
                    await ctx.channel.send(f"El juego actual es: {game_name}")
                else:
                    await ctx.channel.send("No se pudo obtener el juego actual.")
            except requests.RequestException as e:
                print("Error al obtener el juego:", e)
                await ctx.channel.send("No pude obtener el juego. Intenta más tarde.")
        else:
            if user_is_mod or user_is_streamer:
                new_game = ctx.message.content[len("!game "):].strip()
                if not new_game:
                    await ctx.channel.send("Por favor, especifica el nombre del juego que deseas poner.")
                    return

                url = f"https://api.twitch.tv/helix/channels"
                data = {
                    "broadcaster_id": ctx.author.id,
                    "game_name": new_game
                }
                headers = {
                    "Client-ID": CLIENT_ID,
                    "Authorization": f"Bearer {BOT_TOKEN}"
                }

                try:
                    response = requests.patch(url, headers=headers, params=data)
                    response.raise_for_status()

                    if response.status_code == 204:
                        await ctx.channel.send(f"¡El juego ha sido cambiado a: {new_game}!")
                    else:
                        await ctx.channel.send("Hubo un problema al cambiar el juego.")
                except requests.RequestException as e:
                    print("Error al cambiar el juego:", e)
                    await ctx.channel.send("No pude cambiar el juego. Intenta más tarde.")
            else:
                await ctx.channel.send("Solo los moderadores o el streamer pueden cambiar el juego.")
    
    # --- COMANDO !title ---
    @commands.command(name='title')
    async def title(self, ctx, *, new_title=None):
        """
        Comando !title: Muestra o cambia el título del stream.
        """
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "title", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        # Obtener el nombre del canal desde el contexto
        channel_name = ctx.channel.name if hasattr(ctx.channel, 'name') else ctx.channel
        broadcaster_id = await self.get_broadcaster_id(channel_name)
        if not broadcaster_id:
            await ctx.send("No se pudo obtener el ID del canal.")
            return

        if new_title:
            # Verificar si el autor del mensaje es moderador o streamer
            user_is_mod = await self.is_mod(broadcaster_id, ctx.author.id)
            if ctx.author.name.lower() == channel_name.lower() or user_is_mod:
                # Cambiar el título
                headers = {
                    'Client-ID': CLIENT_ID,
                    'Authorization': f'Bearer {BOT_TOKEN}',
                    'Content-Type': 'application/json',
                }
                data = {
                    'title': new_title,
                    'game_id': ''  # Mantén el juego actual si lo deseas
                }
                url = f'https://api.twitch.tv/helix/channels?broadcaster_id={broadcaster_id}'
                try:
                    response = requests.patch(url, headers=headers, json=data)
                    response.raise_for_status()
                    await ctx.send(f"El título del stream ha sido cambiado a: {new_title}")
                except requests.exceptions.RequestException as e:
                    print(f"Error al cambiar el título: {e}")
                    await ctx.send("Hubo un error al cambiar el título del stream.")
            else:
                await ctx.send("No tienes permisos para cambiar el título del stream.")
        else:
            # Mostrar el título actual
            headers = {
                'Client-ID': CLIENT_ID,
                'Authorization': f'Bearer {BOT_TOKEN}',
            }
            url = f'https://api.twitch.tv/helix/channels?broadcaster_id={broadcaster_id}'
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                current_title = data["data"][0]["title"]
                await ctx.send(f"El título actual del stream es: {current_title}")
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener el título: {e}")
                await ctx.send("Hubo un error al obtener el título del stream.")
    
    # Comando !roll
    @commands.command(name='roll')
    async def roll(self, ctx):
        """Genera un número aleatorio entre 0 y 100."""
        cooldown_time = 11
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "roll", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        number = random.randint(0, 100)
        await ctx.channel.send(f"🎲 ¡Has sacado un {number} de 100!")
    
    # Comando !memide
    @commands.command(name='memide')
    async def memide(self, ctx):
        """Calculamos cuanto te mide."""
        cooldown_time = 11
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "memide", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        number = random.randint(0, 50)
        await ctx.channel.send(f"📏 Al usuario {ctx.author.name} le mide {number} cm.")
        
    # Comando !lurk
    @commands.command(name='lurk')
    async def lurk(self, ctx):
        """Ponemos al usuario en modo lurk."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "lurk", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        await ctx.channel.send(f"/me 🕵️‍♂️ {ctx.author.name} está en modo lurk. ¡Gracias por estar ahí!")
    
    # Comando !unlurk
    @commands.command(name='unlurk')
    async def unlurk(self, ctx):
        """Sacamos al usuario del modo lurk."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "unlurk", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        await ctx.channel.send(f"/me 👋 {ctx.author.name} ha salido del modo lurk. ¡Bienvenido de vuelta!")
        
    # Comando !peru para calcular cuánto porcentaje de Perú es el usuario
    @commands.command(name='peru')
    async def peru(self, ctx):
        cooldown_time = 20
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "peru", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        num = random.randint(0, 100)
        await ctx.channel.send(f"Sospecho que {ctx.author.name} es {num}% del Perú 🇵🇪 PogChamp")
        
    # Comando !echo para repetir un mensaje
    @commands.command(name='echo')
    async def echo(self, ctx, *, message):
        cooldown_time = 15
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "echo", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        await ctx.channel.send(message)
    
    @commands.command(name="song")
    async def song(self, ctx: commands.Context):
        """Comando !song para mostrar la canción actual del streamer o de un canal específico."""
        cooldown_time = 15
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "song", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        
        args = ctx.message.content.split()  # Obtener los argumentos del comando
        channel_name = ctx.channel.name  # Obtener el nombre del canal donde se ejecuta el comando
        # Si se especifica un canal, usarlo; de lo contrario, usar el canal actual
        if len(args) > 1:
            target_channel = args[1].lower()  # El canal especificado por el usuario
        else:
            target_channel = channel_name  # El canal actual
        # Obtener el nombre de usuario de Last.fm desde el JSON
        lastfm_username = self.lastfm_channels.get(target_channel, {}).get("username", target_channel)
        # Obtener la canción actual desde Last.fm
        song = await get_current_song(lastfm_username)

        if song:
            await ctx.send(f"🎵 Ahora suena en {target_channel}: {song}")
        else:
            await ctx.send(f"No se encontró ninguna canción en reproducción para {target_channel}.")
        
    @commands.command(name="hug")
    async def hug(self, ctx: commands.Context, user: str):
        """Envía un mensaje de abrazo a un usuario."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "hug", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        if user == None:
            await ctx.send(f"¡@{ctx.author.name} se abrazó a sí mismo! 🤗 maldito virgen.")
            return
        await ctx.send(f"¡@{ctx.author.name} abrazó a @{user}! 🤗")
    
    @commands.command(name="amor")
    async def amor(self, ctx: commands.Context, user: str = None):
        """Comando !amor para calcular la probabilidad de amor entre dos usuarios."""
        cooldown_time = 20
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "amor", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        if not user:
            await ctx.send("Uso correcto: !amor [usuario]")
            return
        author = ctx.author.name
        # Evitar auto-amor
        if user.lower() == author.lower():
            await ctx.send("🤔 ¿Quieres calcular el amor contigo mismo? ¡Eso es 100% de amor propio! 💖")
            return
        
        love_percentage = random.randint(1, 100)
        message = f"💖 La probabilidad de amor entre @{author} y @{user} es del {love_percentage}% 💖"

        # Frases personalizadas según el porcentaje de amor
        if love_percentage < 20:
            message += " 😢 Parece que no hay química..."
        elif love_percentage < 50:
            message += " 😐 Podría ser mejor..."
        elif love_percentage < 80:
            message += " 😊 ¡Hay buena conexión!"
        else:
            message += " 😍 ¡Es amor verdadero!"
        await ctx.send(message)
        
    @commands.command(name="pc", aliases=["specs"])
    async def pc_specs(self, ctx: commands.Context):
        """Comando !pc o !specs para mostrar las especificaciones de la PC del streamer."""
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "pc", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "specs", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        # Seleccionar componentes aleatorios
        procesador = random.choice(procesadores)
        gpu = random.choice(gpus)
        ram = random.choice(rams)
        almacen = random.choice(almacenamiento)
        so = random.choice(sistema_operativo)

        # Construir el mensaje CON EMOJIS
        mensaje = (
            f"Las especificaciones de la PC del streamer son: \n"
            f"🖥️ Procesador: {procesador}\n |"
            f"🎮 GPU: {gpu}\n |"
            f"🧠 RAM: {ram}\n "
            f"💾 Almacenamiento: {almacen} |"
            f"🪟 Sistema Operativo: {so}."
        )
        await ctx.send(mensaje)
    
    # Comando !libra para mostrar informacion sobre $LIBRA
    @commands.command(name="libra")
    async def libra(self, ctx: commands.Context):
        """Comando !libra para mostrar información sobre la criptomoneda $LIBRA."""
        cooldown_time = 60
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "libra", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        mensaje = (
        "🪙 $LIBRA es una criptomoneda lanzada en 2025 dentro del proyecto 'Viva La Libertad', "
        "promovido por Javier Milei para financiar emprendimientos. Tras su lanzamiento, sufrió una fuerte caída, "
        "causando pérdidas y controversias como el actual juicio político a Milei."
    )
        await ctx.send(mensaje)
        
    @commands.command(name="frase")
    async def frase(self, ctx: commands.Context):
        """Comando !frase para mostrar una frase aleatoria."""
        cooldown_time = 11
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "frase", cooldown_time)
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return
        # Seleccionar una frase aleatoria
        frase = random.choice(frases)
        await ctx.send(f"📜 {frase}")
        
    @commands.command(name='donar')
    async def donar(self, ctx: commands.Context):
        """Comando !donar para mostrar el enlace de donación del canal."""
        channel_name = ctx.channel.name.lower()  # Nombre del canal en minúsculas

        # Obtener el enlace de donación del canal
        donation_link = self.donation_links.get(channel_name, self.donation_links.get("default"))

        # Responder con el enlace de donación
        await ctx.send(f"¡Apoya al streamer donando aquí! {donation_link}")
    
# Configurar el cog
def prepare(bot):
    # Verifica si el cog ya está cargado
    for cog in bot.cogs.values():
        if isinstance(cog, GeneralCommands):
            print("GeneralCommands ya está cargado.")
            return
    bot.add_cog(GeneralCommands(bot))