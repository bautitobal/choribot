import json
import os
import random
from twitchio.ext import commands
from utils.cooldown_messages import cooldown_messages
from .cooldown import CooldownManager

class QuoteCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()
        self.quotes_file = "quotes.json"  # Archivo para almacenar las quotes
        self.quotes = self.load_quotes()  # Cargar las quotes al iniciar

    def load_quotes(self):
        """
        Carga las quotes desde el archivo JSON.
        Si el archivo no existe, lo crea con una lista vacía.
        """
        
        
        if not os.path.exists(self.quotes_file):
            with open(self.quotes_file, "w", encoding="utf-8") as file:
                json.dump([], file)  # Crear un archivo con una lista vacía
            return []

        with open(self.quotes_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_quotes(self):
        """
        Guarda las quotes en el archivo JSON.
        """
        with open(self.quotes_file, "w", encoding="utf-8") as file:
            json.dump(self.quotes, file, ensure_ascii=False, indent=4)

    @commands.command(name='quote')
    async def quote(self, ctx):
        """
        Comando !quote: Muestra una quote aleatoria.
        """
        cooldown_time = 30 # Cooldown de 30 segundos
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "quote", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown
        if not self.quotes:
            await ctx.send("No hay quotes disponibles. ¡Usa !addquote para agregar una!")
            return

        # Seleccionar una quote aleatoria
        quote = random.choice(self.quotes)
        await ctx.send(f"📜 Quote #{quote['id']}: {quote['text']} (Creado por {quote['author']})")

    @commands.command(name='addquote')
    async def add_quote(self, ctx, *, text: str):
        """
        Comando !addquote: Agrega una nueva quote.
        """
        cooldown_time = 15 # Cooldown de 15 segundos
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "addquote", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown     
        if not text:
            await ctx.send("Por favor, incluye el texto de la quote.")
            return

        # Crear una nueva quote con un ID único y el nombre del autor
        new_quote = {
            "id": len(self.quotes) + 1,  # El ID es el número de quotes + 1
            "text": text,
            "author": ctx.author.name  # Guardar el nombre del usuario que creó la quote
        }

        # Agregar la quote a la lista
        self.quotes.append(new_quote)
        self.save_quotes()

        await ctx.send(f"✅ Quote #{new_quote['id']} agregada correctamente por {ctx.author.name}.")

    async def is_mod_or_streamer(self, ctx):
        """
        Verifica si el usuario es moderador o el streamer.
        """
        badges = ctx.author.badges
        return "moderator" in badges or "broadcaster" in badges

    @commands.command(name='delquote')
    async def del_quote(self, ctx, quote_id: int):
        """
        Comando !delquote: Elimina una quote por su número.
        Solo moderadores y el streamer pueden usar este comando.
        """
        if not await self.is_mod_or_streamer(ctx):
            await ctx.send("❌ Solo los moderadores o el streamer pueden usar este comando.")
            return

        if not self.quotes:
            await ctx.send("No hay quotes disponibles para eliminar.")
            return

        # Buscar la quote por su ID
        quote_to_delete = None
        for quote in self.quotes:
            if quote["id"] == quote_id:
                quote_to_delete = quote
                break

        if not quote_to_delete:
            await ctx.send(f"❌ No se encontró la quote #{quote_id}.")
            return

        # Eliminar la quote
        self.quotes.remove(quote_to_delete)

        # Actualizar los IDs de las quotes restantes
        for index, quote in enumerate(self.quotes, start=1):
            quote["id"] = index

        self.save_quotes()
        await ctx.send(f"✅ Quote #{quote_id} eliminada correctamente.")