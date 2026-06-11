# 🌤️CheckerWeather - Discord Weather Bot
A simple, modern Discord bot built in Python using `discord.py` and WeatherAPI.com to check tomorrow's weather forecast.

## 🚀 Features
* **Tomorrow's Forecast:** Get detailed weather info for tomorrow including sunrise, sunset, min/max/avg temperatures, and rain chance.
* **Smart Location Management:** Easily change the preferred location globally using a simple slash command. Input is automatically sanitized to handle special characters seamlessly.
* **Production-Grade Error Handling:** Robust custom error architecture that intercepts and handles API errors (e.g., non-existent cities, expired quotas, or invalid keys) without crashing the bot.
* **Automated Daily Notifications:** Automatically broadcasts tomorrow's weather forecast to a designated channel every day at 18:00 Polish Time (Europe/Warsaw).
* **Flexible Channel Setup:** Server administrators can pin a specific channel for daily updates, or let the bot find standard text channels (`weather` / `general`) automatically.

## 🛠️ How to use
The bot uses modern Discord **Slash Commands**. Just type:
* `/tomorrow_weather` - Displays tomorrow's weather forecast for the currently saved city.
* `/change_location [city_name]` - Changes the target city for the weather forecasts.
* `/set_channel [channel]` - Sets a custom text channel for automated daily notifications.
* `/ai [prompt]` - Asks a question to the advanced Ollama Cloud AI model without any local machine overhead.

## 🧰 Tech Stack
* **Language:** Python 3
* **Libraries:** `discord.py` (with App Commands/Slash Commands), `requests`, `tzdata` (for Windows zoneinfo compliance)
* **API Service:** WeatherAPI.com
* **Deployment Platform:** Optimized for Render (Web Services) combined with UptimeRobot for keeping the instance alive.