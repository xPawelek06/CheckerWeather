import os
import threading
import aiohttp
from flask import Flask
from discord.ext import commands, tasks

app = Flask('')
@app.route('/')
def home():
    return "Bot works!"

def run_web_server():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

class KeepAliveCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

        threading.Thread(target=run_web_server, daemon=True).start()
        self.keep_alive_ping.start()

    def cog_unload(self):
        self.keep_alive_ping.cancel()

    @tasks.loop(minutes=10)
    async def keep_alive_ping(self):
        url_render = os.getenv("RENDER_URL")
        if not url_render:
            return
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url_render) as resp:
                    print(resp.status, flush=True)
            except Exception as e:
                print(f"Error while connecting to {url_render} - {e}", flush=True)

async def setup(bot:commands.Bot):
    await bot.add_cog(KeepAliveCog(bot))