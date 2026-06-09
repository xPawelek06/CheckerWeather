import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import requests
from flask import Flask
import threading


app = Flask('')
@app.route('/')
def home():
    return "Bot works!"

def run_web_server():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

load_dotenv()
discord_key = os.getenv("DISCORD_KEY")
weather_key = os.getenv("WEATHER_KEY")

def check_tomorrows_weather():
    url = f"http://api.weatherapi.com/v1/forecast.json?key={weather_key}&q=Lapy&days=2&aqi=no&alerts=no"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data

class CheckerWeather(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix="!", tree_cls=app_commands.CommandTree, **kwargs)

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
        embed.add_field(
            name="**Weather**",
            value="Current weather at",
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

@bot.tree.command(name="tomorrow_weather", description="Shows forecast weather for tomorrow")
async def tomorrow_weather(interaction: discord.Interaction):
    weather_data = check_tomorrows_weather()
    tomorrow = weather_data["forecast"]["forecastday"][1]
    time = tomorrow["date"]
    place = weather_data["location"]["name"]
    max_temp = tomorrow["day"]["maxtemp_c"]
    min_temp = tomorrow["day"]["mintemp_c"]
    avg_temp = tomorrow["day"]["avgtemp_c"]
    rain_chance = tomorrow["day"]["daily_chance_of_rain"]
    sunrise = tomorrow["astro"]["sunrise"]
    sunset = tomorrow["astro"]["sunset"]

    weather_description = f"""
        🌅 **Wschód słońca:** {sunrise}
        🌇 **Zachód słońca:** {sunset}

        🌡️ **Temperatura minimalna:** {min_temp}°C
        🔥 **Temperatura maksymalna:** {max_temp}°C
        📊 **Temperatura średnia:** {avg_temp}°C

        🌧️ **Szansa na deszcz:** {rain_chance}%
        """

    await interaction.response.send_message(
        embed=discord.Embed(
            title=f"Forecast weather {place} - {time}",
            description=weather_description,
            color=discord.Color.blue(),
        )
    )

threading.Thread(target=run_web_server).start()
bot.run(discord_key)