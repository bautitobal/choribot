import aiohttp
import urllib.parse

async def get_world_record(game: str, category: str = None):
    """Obtiene el WR de un juego desde speedrun.com."""
    base_url = "https://www.speedrun.com/api/v1"

    async with aiohttp.ClientSession() as session:
        # Buscar el juego por su nombre o abreviatura
        game_search_url = f"{base_url}/games?name={urllib.parse.quote(game)}"
        async with session.get(game_search_url) as response:
            if response.status != 200:
                return None  # Error en la solicitud

            game_data = await response.json()

        if not game_data.get("data"):
            return None  # No se encontró el juego

        game_id = game_data["data"][0]["id"]
        game_name = game_data["data"][0]["names"]["international"]

        # Obtener las categorías del juego
        categories_url = f"{base_url}/games/{game_id}/categories"
        async with session.get(categories_url) as response:
            if response.status != 200:
                return None  # Error en la solicitud

            categories_data = await response.json()

        if not categories_data.get("data"):
            return None  # No hay categorías

        # Buscar la categoría específica si se proporciona
        selected_category = None
        if category:
            for cat in categories_data["data"]:
                if category.lower() in cat["name"].lower():
                    selected_category = cat
                    break
        else:
            # Tomar la categoría principal (primera en la lista)
            selected_category = categories_data["data"][0]

        if not selected_category:
            return None  # No se encontró la categoría

        category_id = selected_category["id"]
        category_name = selected_category["name"]

        # Obtener el WR de la categoría
        wr_url = f"{base_url}/leaderboards/{game_id}/category/{category_id}?top=1"
        async with session.get(wr_url) as response:
            if response.status != 200:
                return None  # Error en la solicitud

            wr_data = await response.json()

        if not wr_data.get("data", {}).get("runs"):
            return None  # No hay WR en esta categoría

        wr_run = wr_data["data"]["runs"][0]["run"]
        runner_id = wr_run["players"][0]["id"]
        wr_time = wr_run["times"]["primary_t"]

        # Convertir el tiempo de segundos a HH:MM:SS
        hours = int(wr_time // 3600)
        minutes = int((wr_time % 3600) // 60)
        seconds = int(wr_time % 60)
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Obtener el nombre del jugador
        player_url = f"{base_url}/users/{runner_id}"
        async with session.get(player_url) as response:
            if response.status != 200:
                return None  # Error en la solicitud

            player_data = await response.json()

        runner_name = player_data["data"]["names"]["international"]

        return {
            "game": game_name,
            "category": category_name,
            "time": formatted_time,
            "runner": runner_name
        }

async def get_personal_bests(username: str):
    """Obtiene los PBs de un usuario desde speedrun.com."""
    base_url = "https://www.speedrun.com/api/v1"

    async with aiohttp.ClientSession() as session:
        # Buscar los PBs del usuario
        pbs_url = f"{base_url}/users/{urllib.parse.quote(username)}/personal-bests"
        async with session.get(pbs_url) as response:
            if response.status != 200:
                return None  # Error en la solicitud

            pbs_data = await response.json()

        if not pbs_data.get("data"):
            return None  # No se encontraron PBs

        pbs = []
        for run in pbs_data["data"]:
            if not run.get("game") or not run.get("category"):
                continue  # Saltar si falta información

            game_name = run["game"]["data"]["names"]["international"]
            category_name = run["category"]["data"]["name"]
            time = run["times"]["primary_t"]

            # Convertir el tiempo de segundos a HH:MM:SS
            hours = int(time // 3600)
            minutes = int((time % 3600) // 60)
            seconds = int(time % 60)
            formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

            pbs.append({
                "game": game_name,
                "category": category_name,
                "time": formatted_time
            })

        return pbs