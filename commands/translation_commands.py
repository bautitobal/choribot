from twitchio.ext import commands
import requests
import random
from .cooldown import CooldownManager
from utils.cooldown_messages import cooldown_messages

class TranslationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()

    @commands.command(name="traducir")
    async def traducir(self, ctx: commands.Context, *, texto: str = None):
        """
        Comando !traducir para traducir texto.
        Uso: !traducir <idioma_origen>-<idioma_destino> <texto>
        Ejemplo: !traducir es-en Hola
        """
        cooldown_time = 30
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "traducir", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  
        
        if not texto:
            await ctx.send("Uso correcto: !traducir <idioma_origen>-<idioma_destino> <texto>")
            return

        # Separar el par de idiomas y el texto
        partes = texto.split(maxsplit=1)
        if len(partes) < 2:
            await ctx.send("Uso correcto: !traducir <idioma_origen>-<idioma_destino> <texto>")
            return

        idiomas, texto_a_traducir = partes

        # Separar idioma de origen y destino
        if '-' not in idiomas:
            await ctx.send("Formato incorrecto. Usa: !traducir <idioma_origen>-<idioma_destino> <texto>")
            return

        idioma_origen, idioma_destino = idiomas.split('-')

        # Llamar a la API de MyMemory
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": texto_a_traducir,
            "langpair": f"{idioma_origen}|{idioma_destino}",  # Especificar idioma de origen y destino
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa

            # Procesar la respuesta de la API
            data = response.json()
            if "responseData" in data and "translatedText" in data["responseData"]:
                traduccion = data["responseData"]["translatedText"]
                await ctx.send(f"🤖 Traducción: {traduccion}")
            else:
                await ctx.send("No se pudo traducir el texto. Intenta de nuevo más tarde.")
        except requests.exceptions.RequestException as e:
            print(f"Error al traducir: {e}")
            await ctx.send("Hubo un error al traducir el texto. Intenta de nuevo más tarde.")