import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from cogs.weather import CITIES_FIX

load_dotenv()
discord_key = os.getenv("DISCORD_KEY")
weather_key = os.getenv("WEATHER_KEY")

class CheckerWeather(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix="!", tree_cls=app_commands.CommandTree, **kwargs)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog {filename}")

    async def on_ready(self):
        synced_slash_commands = await self.tree.sync()
        print(f"Logged in as {self.user}")
        print(f"Synchronized {len(synced_slash_commands)} slash commands!")

    async def on_guild_join(self, guild: discord.Guild):
        current_location = "Łapy"

        weather_cog = self.get_cog("WeatherCog")
        if weather_cog and hasattr(weather_cog, 'location'):
            location = weather_cog.location
            current_location = CITIES_FIX.get(location, location)


        command_list = f"""
`/current_weather` - Displays live weather reports enhanced with a custom AI poem and outfit recommendations.
`/tomorrow_weather` - Displays tomorrow's weather forecast for the currently saved city.
`/change_location [city_name]` - Changes the target city for the weather forecasts.
`/set_channel [channel]` - Sets a custom text channel for automated daily notifications. 
"""

        embed = discord.Embed(
            title="🌤️ Welcome to CheckerWeather!",
            description="Thanks for adding CheckerWeather to your Discord server! I'm here to keep you updated on tomorrow's weather forecast.",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="📜 Command List:",
            value=command_list,
            inline=False,
        )
        embed.add_field(
            name="📍 Current Default Location",
            value=f"The bot is currently set to **{current_location}**. Use `/change_location` to update it!",
            inline=False,
        )
        embed.add_field(
            name="⚙️ Automated Daily Notifications Setup",
            value=(
                "To choose exactly where the bot should post daily forecasts, use the **`/set_channel`** command.\n\n"
                "⚠️ *If you don't set a custom channel, the bot will automatically try to find a text channel named "
                "**`weather`** or **`general`**. If none of those exist, it will use the first available "
                "channel it has permission to send messages to.*"
            ),
            inline=False,
        )
        if self.user.avatar:
            embed.set_footer(text="CheckerWeather • Created with passion", icon_url=self.user.avatar.url)
        else:
            embed.set_footer(text="CheckerWeather • Created with passion")

        bot_member = guild.get_member(self.user.id) or await guild.fetch_member(self.user.id)
        if not bot_member:
            return

        for channel in sorted(guild.text_channels, key=lambda c: c.position):
            bot_permissions = channel.permissions_for(bot_member)
            if bot_permissions.send_messages and bot_permissions.embed_links:
                try:
                    await channel.send(embed=embed)
                    break
                except discord.Forbidden:
                    continue
                except Exception as e:
                    print(f"Error during sending embed on channel {channel.name}: {e}", flush=True)
                    continue

intents = discord.Intents.default()
intents.guilds = True
bot = CheckerWeather(intents=intents)

bot.run(discord_key)