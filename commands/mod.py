from twitchio.ext import commands

class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_moderator(self, ctx: commands.Context):
        """Verifica si el usuario que ejecuta el comando es moderador."""
        # Obtener los badges del usuario
        badges = ctx.author.badges
        # Verificar si el usuario es moderador o el streamer
        return "moderator" in badges or "broadcaster" in badges

    @commands.command(name="ban")
    async def ban(self, ctx: commands.Context, user: str, reason: str = "Sin razón especificada"):
        """Comando !ban para banear a un usuario."""
        if not await self.is_moderator(ctx):
            await ctx.send("❌ Solo los moderadores pueden usar este comando.")
            return

        # Banear al usuario usando el comando de Twitch
        await ctx.send(f"/ban {user} {reason}")
        #await ctx.send(f"🔨 @{user} ha sido baneado. Razón: {reason}")

    @commands.command(name="timeout")
    async def timeout(self, ctx: commands.Context, user: str, duration: int, reason: str = "Sin razón especificada"):
        """Comando !timeout para dar timeout a un usuario."""
        if not await self.is_moderator(ctx):
            await ctx.send("❌ Solo los moderadores pueden usar este comando.")
            return

        # Validar la duración del timeout (máximo 1,209,600 segundos = 2 semanas)
        if duration < 1 or duration > 1209600:
            await ctx.send("❌ La duración del timeout debe estar entre 1 y 1,209,600 segundos.")
            return

        # Dar timeout al usuario usando el comando de Twitch
        await ctx.send(f"/timeout {user} {duration} {reason}")
        #await ctx.send(f"⏳ @{user} ha recibido un timeout de {duration} segundos. Razón: {reason}")

# Configurar el cog
def prepare(bot):
    bot.add_cog(ModCommands(bot))