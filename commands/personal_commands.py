from twitchio.ext import commands
from .cooldown import CooldownManager
from utils.cooldown_messages import cooldown_messages
import random

class PersonalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()

    async def is_allowed_channel(self, ctx: commands.Context):
        """Verifica si el comando se ejecuta en un canal permitido."""
        return ctx.channel.name.lower() in ["choripanycristi", "choribot11"]

    @commands.command(name="discord")
    async def discord(self, ctx: commands.Context):
        """Muestra el enlace al servidor de Discord."""
        cooldown_time = 30 
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "discord", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown
        
        
        if not await self.is_allowed_channel(ctx):
            return  # No hacer nada si no es un canal permitido

        await ctx.send("¡Únete a nuestro servidor de Discord! https://discord.gg/4hf9F53")

    @commands.command(name="socials")
    async def socials(self, ctx: commands.Context):
        """Muestra los enlaces a las redes sociales."""
        
        cooldown_time = 15 
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "socials", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown
        
        if not await self.is_allowed_channel(ctx):
            return  # No hacer nada si no es un canal permitido

        await ctx.send(
            "¡Síguenos en nuestras redes sociales! \n"
            "Twitter: https://x.com/choripanycristi\n "
            "Instagram: https://instagram.com/chorycristi\n "
            "YouTube: https://youtube.com/@choripanycristi\n"
            "Tiktok: https://tiktok.com/@choripanycristi "
        )

    @commands.command(name="shar")
    async def shar(self, ctx: commands.Context):
        """Muestra información sobre el juego SHAR."""
        cooldown_time = 60  # Cooldown de 60 segundos
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "shar", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown
        if not await self.is_allowed_channel(ctx):
            return  # No hacer nada si no es un canal permitido

        await ctx.send(
            "¡Juega a The Simpsons Hit & Run (SHAR) y únete a la comunidad!\n "
            "| SHAR Discord: https://discord.gg/nU48TVd \n"
            "| SHAR Wiki: https://sharwiki.com/"
        )

    @commands.command(name="pikuniku")
    async def pikuniku(self, ctx: commands.Context):
        """Muestra información sobre el juego Pikuniku."""
        cooldown_time = 60  # Cooldown de 60 segundos
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "pikuniku", cooldown_time)
        
        if cooldown_status is not False:  # Si hay cooldown
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown
        
        if not await self.is_allowed_channel(ctx):
            return  # No hacer nada si no es un canal permitido
        await ctx.channel.send("Pikuniku is a game about an red ball with legs that saves the world from a capitalist regime. Pikuniku Speedrunning Discord -> https://discord.gg/6CBMA6S")

# Configurar el cog
def prepare(bot):
    bot.add_cog(PersonalCommands(bot))
