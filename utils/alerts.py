class Alerts:
    @staticmethod
    async def on_follow(ctx, user):
        """Mensaje de alerta cuando un usuario sigue el canal."""
        await ctx.send(f"🎉 ¡Gracias por el follow, {user.name} amigo! 🎉")

    @staticmethod
    async def on_subscription(ctx, user, tier, message):
        """Mensaje de alerta cuando un usuario se suscribe al canal."""
        tier_name = {
            1: "Tier 1",
            2: "Tier 2",
            3: "Tier 3"
        }.get(tier, "Tier Desconocido")
        await ctx.send(f"🌟 ¡{user.name} se ha suscrito con {tier_name}! ¡Gracias! 🌟")

    @staticmethod
    async def on_resubscription(ctx, user, tier, months, message):
        """Mensaje de alerta cuando un usuario renueva su suscripción."""
        tier_name = {
            1: "Tier 1",
            2: "Tier 2",
            3: "Tier 3"
        }.get(tier, "Tier Desconocido")
        await ctx.send(f"🌟 ¡{user.name} ha renovado su suscripción {tier_name} por {months} meses! ¡Gracias amigo! 🌟")

    @staticmethod
    async def on_donation(ctx, user, amount, message):
        """Mensaje de alerta cuando un usuario dona."""
        await ctx.send(f"💰 ¡{user.name} ha donado ${amount:.2f}! ¡Gracias por tu generosidad respeto máximo! 💰")

    @staticmethod
    async def on_cheer(ctx, user, bits, message):
        """Mensaje de alerta cuando un usuario hace un cheer."""
        await ctx.send(f"🎉 ¡{user.name} ha enviado {bits} bits! ¡Gracias por el apoyo respeto máximo! 🎉")

    @staticmethod
    async def on_raid(ctx, raider, viewers):
        """Mensaje de alerta cuando un canal hace un raid."""
        await ctx.send(f"🚨 ¡{raider.name} ha hecho un raid con {viewers} espectadores! ¡Bienvenidos! 🚨")

def prepare(bot):
    bot.add_cog(Alerts(bot))