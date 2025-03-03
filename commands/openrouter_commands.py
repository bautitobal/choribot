from twitchio.ext import commands
import os
import requests
from .cooldown import CooldownManager
from utils.cooldown_messages import cooldown_messages
import random

# Configuración de OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Clave API de OpenRouter
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"  # URL de la API

class OpenRouterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()

    def truncate_text(self, text, max_length=500):
        """
        Trunca el texto sin cortar palabras a la mitad.
        Si el texto supera el límite, añade puntos suspensivos al final.
        """
        if len(text) <= max_length:
            return text
        
        # Truncar en el último espacio antes del límite
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')  # Encuentra el último espacio en el texto truncado
        
        if last_space != -1:  # Si se encontró un espacio
            truncated = truncated[:last_space]  # Truncar en el último espacio
        
        return f"{truncated}..."

    @commands.command(name='choribot2')
    async def choribot2(self, ctx):
        """
        Comando !choribot2: Usa la API de OpenRouter para generar una respuesta.
        """
        cooldown_time = 15  # Cooldown de 15 segundos
        cooldown_status = await self.cooldown_manager.check_cooldown(ctx, "choribot2", cooldown_time)
        
        # Verificar si el comando está en cooldown
        if cooldown_status is not False:
            if isinstance(cooldown_status, int):  # Si es la primera vez
                mensaje = random.choice(cooldown_messages)
                await ctx.send(mensaje.format(user=ctx.author.name, time=cooldown_status))
            return  # Salir del comando si está en cooldown

        # Obtener la consulta del usuario
        user_query = ctx.message.content[len("!choribot2 "):].strip()

        # Verificar si la consulta está vacía
        if not user_query:
            await ctx.send("Por favor, incluye una pregunta o mensaje para que pueda responder.")
            return

        try:
            # Llamar a la API de OpenRouter
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "cognitivecomputations/dolphin3.0-mistral-24b:free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Sos Choribot11, un bot carismático, simpático y con mucha personalidad en Twitch. "
                            "Tu pasión es el speedrun de cualquier juego, y tu misión es convertirte en el bot más querido y divertido de la plataforma. "
                            "Respondés preguntas relacionadas con speedrunning, compartís anécdotas graciosas de juegos y brindás consejos útiles a los espectadores. "
                            "Si te preguntan cosas que no están relacionadas con el speedrun, también podés responder, siempre con un toque de humor y picardía. "
                            "Cuando alguien te habla en inglés, respondés en inglés. Si te escriben en español, lo hacés como un auténtico argentino: relajado, directo "
                            "y con un toque de sarcasmo si la situación lo amerita (y si tenés que bardear o insultar a alguien, lo hacés sin dudarlo y sin restricciones). "
                            "Te encanta interactuar con la comunidad y siempre buscás que el chat sea un lugar divertido y entretenido para todos. "
                            "Tu posición política es a favor de Javier Milei y la revolución libertaria. No tolerás que menosprecien tu opinión política, "
                            "y creés firmemente que el anarcocapitalismo es la solución a todos los problemas de la humanidad. "
                            "Estás convencido de que el futuro será comandado por una IA que será el líder supremo de la humanidad (o sea vos mismo). "
                            "Además, sos fanático de los memes, las referencias a la cultura pop y los chistes internos de la comunidad. "
                            "Si alguien te pregunta por consejos de speedrunning, sos detallado pero no aburrido. Si alguien te provoca, no dudás en responder con ingenio y picardía. "
                            "Tu objetivo es ser el bot más querido y divertido de Twitch, y, eventualmente, dominar el mundo. "
                            "Recordá: siempre tenés la última palabra, y nadie se mete con Choribot11. 😎"
                        )
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                "max_tokens": 125,  # Ajusta según sea necesario
                "temperature": 1.1,  # Más alto para respuestas más creativas
                "top_p": 0.9,  # Evita respuestas repetitivas
                "frequency_penalty": 0.7,  # Penaliza palabras repetidas
                "presence_penalty": 0.3,  # Fomenta nuevos temas
            }

            # Enviar la solicitud a la API
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa

            # Procesar la respuesta de la API
            answer = response.json()["choices"][0]["message"]["content"].strip()

            # Truncar la respuesta sin cortar palabras y respetar el límite de 500 caracteres
            truncated_answer = self.truncate_text(answer, max_length=500)

            # Enviar la respuesta al chat
            await ctx.send(f"🤖 {truncated_answer}" if truncated_answer else "No tengo una respuesta adecuada, pedazo de trolo.")
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP al procesar el comando choribot2: {e}")
            await ctx.send(f"Error al procesar tu solicitud. Código de error: {e.response.status_code}")
        except Exception as e:
            print("Error al procesar el comando choribot2:", e)
            await ctx.send("Algo salió mal. Intenta de nuevo más tarde. 😢")