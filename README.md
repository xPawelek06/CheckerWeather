# 🌤️CheckerWeather - Discord Weather Bot
A simple, modern Discord bot built in Python using `discord.py` and WeatherAPI.com to check tomorrow's weather forecast.

## 🚀 Features
* **Tomorrow's Forecast:** Get detailed weather info for tomorrow including sunrise, sunset, min/max/avg temperatures, and rain chance.
* **Location Management:** Easily change the preferred location globally using a simple slash command.
* **Character Support:** Automatically sanitizes input and handles special characters seamlessly.

## 🛠️ How to use
The bot uses modern Discord **Slash Commands**. Just type:
* `/tomorrow_weather` - Displays tomorrow's weather forecast for the currently saved city.
* `/change_location [city_name]` - Changes the target city for the weather forecasts.

## 🧰 Tech Stack
* Python 3
* `discord.py` (with App Commands)
* WeatherAPI