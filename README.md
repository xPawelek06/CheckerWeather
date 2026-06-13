# 🌤️CheckerWeather - Discord Weather Bot
A simple, modern Discord bot built in Python using `discord.py` and WeatherAPI.com to check tomorrow's weather forecast.

## 🚀 Features
* **Real-Time Weather Report:** Get detailed, live weather conditions, including cloud cover, wind speed, wind direction, and rain probability using `/current_weather`.
* **AI-Powered Insights:** Integrated with the Ollama API, the bot generates a unique, beautifully crafted four-line poem and practical clothing suggestions based on live weather data.
* **Tomorrow's Forecast:** Stay ahead with automated or manual queries (`/tomorrow_weather`) for tomorrow's detailed info, including sunrise, sunset, and temperature metrics.
* **Smart Location Management:** Easily change the preferred location globally using a simple slash command. Input is automatically sanitized to handle special characters seamlessly.
* **Production-Grade Error Handling:** Robust custom error architecture that intercepts and handles API or LLM errors (e.g., non-existent cities, expired quotas, or invalid keys) without crashing the bot.
* **Automated Daily Notifications:** Automatically broadcasts tomorrow's weather forecast to a designated channel every day at 16:00 UTC.
* **Flexible Channel Setup:** Server administrators can pin a specific channel for daily updates via a command, backed by a persistent PostgreSQL database, or let the bot find standard text channels (`weather` / `general`) automatically.

## 🛠️ How to use
The bot uses modern Discord **Slash Commands**. Just type:
* `/current_weather` - Displays live weather reports enhanced with a custom AI poem and outfit recommendations.
* `/tomorrow_weather` - Displays tomorrow's weather forecast for the currently saved city.
* `/change_location [city_name]` - Changes the target city for the weather forecasts.
* `/set_channel [channel]` - Sets a custom text channel for automated daily notifications (Requires `Manage Server` permissions).

## 🧰 Tech Stack
* **Language:** Python 3
* **Libraries:** `discord.py` (with App Commands/Slash Commands), `requests`, `asyncpg` (PostgreSQL client), `ollama` (AsyncClient for AI integration)
* **Database:** PostgreSQL (for persistent server-side channel configuration)
* **AI Engine:** Ollama Cloud Engine (`gemma4:31b`)
* **API Service:** WeatherAPI.com
* **Deployment Platform:** Optimized for Render (Web Services) combined with UptimeRobot for keeping the instance alive.

## ⚡ Invite the Bot
👉 **[Click here to invite CheckerWeather to your Discord server!](https://discord.com/oauth2/authorize?client_id=1513504909784387755)**
