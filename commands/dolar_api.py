import aiohttp
from twitchio.ext import commands

class DolarCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://dolarapi.com/v1/dolares"

    @commands.command(name='dolar')
    async def dolar(self, ctx):
        """
        Comando !dolar: Muestra las cotizaciones de los distintos tipos de dólar.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Formatear la respuesta
                        message = "💵 Cotizaciones del dólar\n "
                        for dolar in data:
                            message += (
                                f"{dolar['nombre']}: "
                                f"Compra: ${dolar['compra']} | "
                                f"Venta: ${dolar['venta']} | 💵\n "
                            )

                        await ctx.send(message)
                    else:
                        await ctx.send("❌ No se pudo obtener la información del dólar. Intenta de nuevo más tarde.")
        except Exception as e:
            print(f"Error al obtener las cotizaciones del dólar: {e}")
            await ctx.send("❌ Ocurrió un error al obtener las cotizaciones del dólar.")