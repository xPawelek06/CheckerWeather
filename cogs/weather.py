import discord
from discord.ext import commands
from discord import app_commands
import os
import requests
import unicodedata

POLISH_CITIES_FIX = {
    "Lapy": "Łapy",
    "Bialystok": "Białystok",
    "Karkow": "Kraków",
    "Poznan": "Poznań",
    "Gdansk": "Gdańsk",
    "Wroclaw": "Wrocław",
    "Lodz": "Łódź",
}

def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize('NFD', text)
    cleaned = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')
    cleaned = cleaned.replace('Ł', 'L').replace('ł', 'l')
    return cleaned

class WeatherCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.location = "Lapy"

    def check_tomorrows_weather(self):
        weather_key = os.getenv("WEATHER_KEY")
        url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_key}&q={self.location}&days=2&aqi=no&alerts=no"
        response = requests.get(url)
        weather_data = response.json()
        return weather_data

    @app_commands.command(name="tomorrow_weather", description="Shows forecast weather for tomorrow")
    async def tomorrow_weather(self, interaction: discord.Interaction):
        weather_data = self.check_tomorrows_weather()
        tomorrow = weather_data["forecast"]["forecastday"][1]
        time = tomorrow["date"]
        raw_place = weather_data["location"]["name"]
        place = POLISH_CITIES_FIX.get(raw_place, raw_place)
        max_temp = tomorrow["day"]["maxtemp_c"]
        min_temp = tomorrow["day"]["mintemp_c"]
        avg_temp = tomorrow["day"]["avgtemp_c"]
        rain_chance = tomorrow["day"]["daily_chance_of_rain"]
        sunrise = tomorrow["astro"]["sunrise"]
        sunset = tomorrow["astro"]["sunset"]

        weather_description = f"""
🌅 **Sunrise:** {sunrise}
🌇 **Sunset:** {sunset}

🌡️ **Minimum temperature:** {min_temp}°C
🔥 **Maximum temperature:** {max_temp}°C
📊 **Average temperature:** {avg_temp}°C

🌧️ **Rain chance:** {rain_chance}%
"""

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"Forecast weather: {place} - {time}",
                description=weather_description,
                color=discord.Color.blue(),
            )
        )

    @app_commands.command(name="change_location", description="Change selected location")
    async def change_location(self, interaction: discord.Interaction, location: str):
        cleaned_location = remove_accents(location)
        self.location = cleaned_location

        await interaction.response.send_message(f"You location has been changed to {location}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WeatherCog(bot))