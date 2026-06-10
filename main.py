import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

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
        await self.tree.sync()
        print(f"Logged in as {self.user}")
        print(f"Synchronized {len(self.commands)} commands!")

    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(
            title="Welcome to CheckerWeather!",
            description="Thanks for using CheckerWeather on your discord server!",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Command List:",
            value="Pogoda_jutro",
            inline=False,
        )

        for channel in sorted(guild.text_channels, key=lambda c: c.position):
            bot_permissions = channel.permissions_for(guild.me)
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
intents.message_content = True
intents.guilds = True
intents.members = True
bot = CheckerWeather(intents=intents)

bot.run(discord_key)