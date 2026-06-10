import discord
from discord.ext import commands
from discord import app_commands
import os
import requests

def check_tomorrows_weather():
    weather_key = os.getenv("WEATHER_KEY")
    url = f"http://api.weatherapi.com/v1/forecast.json?key={weather_key}&q=Lapy&days=2&aqi=no&alerts=no"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data

class WeatherCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tomorrow_weather", description="Shows forecast weather for tomorrow")
    async def tomorrow_weather(self, interaction: discord.Interaction):
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

🌡️ **Minimalna temperatura:** {min_temp}°C
🔥 **Maksymalna temperatura:** {max_temp}°C
📊 **Średnia temperatura:** {avg_temp}°C

🌧️ **Szansa na deszcz:** {rain_chance}%
"""

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"Forecast weather {place} - {time}",
                description=weather_description,
                color=discord.Color.blue(),
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(WeatherCog(bot))