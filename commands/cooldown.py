import time

class CooldownManager:
    def __init__(self):
        self.cooldowns = {}  # Diccionario para almacenar los cooldowns

    async def check_cooldown(self, ctx, command_name, cooldown_time):
        """Verifica si el comando está en cooldown para el usuario."""
        user_id = ctx.author.id
        key = f"{user_id}_{command_name}"
        current_time = time.time()

        if key in self.cooldowns:
            last_used, message_sent = self.cooldowns[key]
            if current_time - last_used < cooldown_time:
                if not message_sent:  
                    remaining_time = int(cooldown_time - (current_time - last_used))
                    self.cooldowns[key] = (last_used, True)  # Marcar que el mensaje ya se envió
                    return remaining_time  # Devuelve el tiempo restante
                return None 
            else:
                # Si el cooldown ha terminado, reiniciar el estado
                del self.cooldowns[key]

        self.cooldowns[key] = (current_time, False)  # Reiniciar el cooldown
        return False  