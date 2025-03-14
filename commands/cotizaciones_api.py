import aiohttp
from twitchio.ext import commands

class CotizacionesCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apis = {
            "argentina": "https://dolarapi.com/v1/cotizaciones",
            "uruguay": "https://uy.dolarapi.com/v1/cotizaciones",
            "chile": "https://cl.dolarapi.com/v1/cotizaciones",
            "brasil": "https://br.dolarapi.com/v1/cotacoes",
            "mexico": "https://mx.dolarapi.com/v1/cotizaciones",
        }
        self.paises_disponibles = list(self.apis.keys())

    @commands.command(name='cotizacion')
    async def cotizacion(self, ctx, pais: str = None):
        """
        Comando !cotizacion: Muestra las cotizaciones de las monedas para el país especificado.
        """
        if not pais or pais.lower() not in self.paises_disponibles:
            # Mostrar la lista de países disponibles
            await ctx.send(
                f"❌ País no válido. Países disponibles: {', '.join(self.paises_disponibles)}. "
                f"Usa el comando así: !cotizacion [país]"
            )
            return

        pais = pais.lower()
        api_url = self.apis[pais]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Formatear la respuesta
                        message = f"💵 Cotizaciones en {pais.capitalize()}:\n "
                        for cotizacion in data:
                            nombre = cotizacion.get("nombre", "Desconocido")  
                            nome = cotizacion.get("nome", "Desconocido")
                            compra = cotizacion.get("compra", "N/A")
                            venta = cotizacion.get("venta", "N/A")
                            venda = cotizacion.get("venda", "N/A")
                            if (pais == "brasil"):
                                message += (
                                    f"{nome}: "
                                    f"Compra: {compra} | "
                                    f"Venta: {venda}\n 💵 "
                                )
                            message += (
                                f"{nombre}: "
                                f"Compra: {compra} | "
                                f"Venta: {venta}\n 💵 "
                            )

                        await ctx.send(message)
                    else:
                        await ctx.send(f"❌ No se pudo obtener la información de {pais.capitalize()}. Intenta de nuevo más tarde.")
        except Exception as e:
            print(f"Error al obtener las cotizaciones de {pais}: {e}")
            await ctx.send(f"❌ Ocurrió un error al obtener las cotizaciones de {pais.capitalize()}.")