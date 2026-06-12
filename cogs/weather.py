import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import requests
import unicodedata
from datetime import time
from zoneinfo import ZoneInfo
import asyncpg

CITIES_FIX = {
    "Lapy": "Łapy",
    "Bialystok": "Białystok",
    "Poznan": "Poznań",
    "Gdansk": "Gdańsk",
    "Wroclaw": "Wrocław",
    "Lodz": "Łódź",
    "Krakow": "Kraków"
}

def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize('NFD', text)
    cleaned = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')
    cleaned = cleaned.replace('Ł', 'L').replace('ł', 'l')
    return cleaned

class WeatherAPIError(Exception):
    def __init__(self, message: str, error_code: int=None):
        super().__init__(message)
        self.error_code = error_code

class WeatherCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.location = "Lapy"
        self.forecast_channels = {}
        self.db_pool = None

    async def cog_load(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("[WeatherCog] BŁĄD: Brak zmiennej DATABASE_URL w pliku .env!")
            return

        try:
            # Tworzymy stabilną pulę połączeń z bazy danych
            self.db_pool = await asyncpg.create_pool(db_url)

            # Tworzymy tabelę w bazie, o ile nie została stworzona wcześniej
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS weather_channels (
                        guild_id BIGINT PRIMARY KEY,
                        channel_id BIGINT NOT NULL
                    )
                ''')

                # Pobieramy zapisane kanały i wrzucamy je do pamięci podręcznej bota
                rows = await conn.fetch('SELECT guild_id, channel_id FROM weather_channels')
                for row in rows:
                    self.forecast_channels[row['guild_id']] = row['channel_id']

            print("[WeatherCog] Pomyślnie połączono z PostgreSQL i wczytano konfigurację kanałów.")
        except Exception as e:
            print(f"[WeatherCog] Krytyczny błąd połączenia z bazą danych: {e}")

        # Czekamy, aż bot połączy się w pełni z Discordem, zanim uruchomimy pętlę czasu
        if not self.daily_weather_notification.is_running():
            self.bot.loop.create_task(self._start_loop_when_ready())

    async def _start_loop_when_ready(self):
        await self.bot.wait_until_ready()
        self.daily_weather_notification.start()
        print("[WeatherCog] Bot jest gotowy. Pętla powiadomień pogodowych została uruchomiona.")

    def cog_unload(self):
        self.daily_weather_notification.stop()
        # Bezpieczne zamykanie połączeń z bazą przy zamykaniu coga
        if self.db_pool:
            self.bot.loop.create_task(self.db_pool.close())
            print("[WeatherCog] Połączenie z bazą PostgreSQL zostało zamknięte.")

    def check_tomorrows_weather(self):
        weather_key = os.getenv("WEATHER_KEY")
        url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_key}&q={self.location}&days=2&aqi=no&alerts=no"
        response = requests.get(url)

        if response.status_code == 200:
            weather_data = response.json()
            return weather_data

        try:
            error_data = response.json().get("error", {})
            api_code = error_data.get("code")
            api_msg = error_data.get("message")
        except Exception:
            api_code = None
            api_msg = "Unknown API error"

        if response.status_code == 400:
            if api_code == 1006:
                raise WeatherAPIError(f"Did not found localization named: **{self.location}**.", api_code)
            raise WeatherAPIError(f"Invalid API question (Code: {api_code}): {api_msg}.", api_code)

        elif response.status_code == 401:
            raise WeatherAPIError("API Key is invalid or did not mentioned. Check bot configuration.", api_code)

        elif response.status_code == 403:
            if api_code == 2007:
                raise WeatherAPIError("Free question's limit on this month has been used.", api_code)
            raise WeatherAPIError("API access has been blocked", api_code)

        else:
            raise WeatherAPIError(f"Weather server error (HTTP {response.status_code}): {api_msg}.", api_code)

    @tasks.loop(time=time(hour=11, minute=10, second=0, tzinfo=ZoneInfo("Europe/Warsaw")))
    async def daily_weather_notification(self):

        try:
            weather_data = self.check_tomorrows_weather()
            tomorrow = weather_data["forecast"]["forecastday"][1]
            forecast_date = tomorrow["date"]
            raw_place = weather_data["location"]["name"]
            place = CITIES_FIX.get(raw_place, raw_place)
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

            embed = discord.Embed(
                title=f"🔔 Daily Forecast: {place} - {forecast_date}",
                description=weather_description,
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Automated daily notification")

            for guild in self.bot.guilds:
                channel_id = self.forecast_channels.get(guild.id)
                channel = None

                if channel_id:
                    channel = guild.get_channel(channel_id)

                if not channel:
                    channel = discord.utils.get(guild.text_channels, name="weather")
                if not channel:
                    channel = discord.utils.get(guild.text_channels, name="general")

                if channel and isinstance(channel, discord.TextChannel):
                    bot_permissions = channel.permissions_for(guild.me)
                    if bot_permissions.send_messages and bot_permissions.embed_links:
                        try:
                            await channel.send(embed=embed)
                            print(f"Successfully sent message on server {guild.name}(channel: {channel.name}).")

                        except Exception as e:
                            print(f"Failed to send message on server {guild.name}:{e}")

        except Exception as e:
            print(f"Failed while getting weather data: {e}")

    @app_commands.command(name="tomorrow_weather", description="Shows forecast weather for tomorrow")
    async def tomorrow_weather(self, interaction: discord.Interaction):
        try:
            weather_data = self.check_tomorrows_weather()
            tomorrow = weather_data["forecast"]["forecastday"][1]
            forecast_date = tomorrow["date"]
            raw_place = weather_data["location"]["name"]
            place = CITIES_FIX.get(raw_place, raw_place)
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
                    title=f"Forecast weather: {place} - {forecast_date}",
                    description=weather_description,
                    color=discord.Color.blue(),
                )
            )

        except WeatherAPIError as e:
            await interaction.response.send_message(
                f"⚠️ **The weather problem:** {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "❌ An unexpected error occurred whilst attempting to retrieve the weather forecast.",
                ephemeral=True
            )
            print(e)

    @app_commands.command(name="current_weather", description="Shows current weather")
    async def current_weather(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        try:
            weather_data = self.check_tomorrows_weather()
            current_time = weather_data["location"]["localtime"]
            current_place = weather_data["location"]["name"]
            place = CITIES_FIX.get(current_place, current_place)
            today = weather_data["current"]
            temp_c = today["temp_c"]
            cloud = today["cloud"]
            wind_speed = today["wind_kph"]
            wind_direction = today["wind_dir"]
            weather_condition = today.get("condition", {}).get("text", "N/A")

            time_part = current_time.split()[-1]
            current_hour = int(time_part.split(":")[0])
            rain_chance = weather_data["forecast"]["forecastday"][0]["hour"][current_hour]["chance_of_rain"]

            weather_description = (
            f"### 🌍 Location: **{place}**\n"
            f"🕒 *Local report time: {current_time}*\n\n"
            f"🌡️ **Temperature:** `{temp_c}°C`\n"
            f"☁️ **Cloud Cover:** `{cloud}%` ({weather_condition})\n"
            f"💧 **Chance of Rain:** `{rain_chance}%`\n"
            f"💨 **Wind:** `{wind_speed} kph` direction `[{wind_direction}]`"
            )

            embed = discord.Embed(
                title=f"🌤️ Current Weather Report",
                description=weather_description,
                color=discord.Color.blue(),
            )
            if "condition" in today and "icon" in today["condition"]:
                icon_url = f"https:{today['condition']['icon']}"
                embed.set_thumbnail(url=icon_url)

            embed.set_footer(text="CheckerWeather • Live Data")

            await interaction.followup.send(embed=embed)

        except WeatherAPIError as e:
            await interaction.followup.send(f"⚠️ **The weather problem:** {str(e)}")
        except Exception as e:
            await interaction.followup.send("❌ An unexpected error occurred whilst attempting to retrieve the weather forecast.")
            print(e)

    @app_commands.command(name="change_location", description="Change selected location")
    async def change_location(self, interaction: discord.Interaction, location: str):
        old_location = self.location

        try:
            cleaned_location = remove_accents(location)
            self.location = cleaned_location

            await interaction.response.defer(ephemeral=True)

            self.check_tomorrows_weather()
            display_name = CITIES_FIX.get(cleaned_location, location)
            await interaction.followup.send(
                f"🎯 Your location has been successfully changed to **{display_name}**.",
                ephemeral=True
            )

        except WeatherAPIError as e:
            self.location = old_location

            await interaction.followup.send(
                f"⚠️ **Could not change location:** {str(e)}",
                ephemeral=True
            )

        except Exception as e:
            self.location = old_location
            await interaction.followup.send(
                "❌ An unexpected error occurred while verifying the new location. Changes reverted.",
                ephemeral=True
            )

    @app_commands.command(name="set_channel", description="Set the channel where daily weather updates will be sent")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild_id:
            await interaction.response.send_message("This command can only be used inside a server.", ephemeral=True)
            return

        self.forecast_channels[interaction.guild_id] = channel.id
        if self.db_pool:
            try:
                async with self.db_pool.acquire() as conn:
                    await conn.execute('''
                                INSERT INTO weather_channels (guild_id, channel_id)
                                VALUES ($1, $2)
                                ON CONFLICT (guild_id) 
                                DO UPDATE SET channel_id = EXCLUDED.channel_id
                            ''', interaction.guild_id, channel.id)
                print(f"[Database] Zaktualizowano kanał powiadomień dla serwera o ID: {interaction.guild_id}")
            except Exception as e:
                print(f"[Database] Błąd podczas zapisu kanału powiadomień: {e}")

        await interaction.response.send_message(
            f"🎯 Daily weather forecasts will now be sent to {channel.mention}!",
            ephemeral=True
        )

    @set_channel.error
    async def set_channel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need `Manage Server` permissions to use this command.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(WeatherCog(bot))