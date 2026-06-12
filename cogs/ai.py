import discord
from discord.ext import commands
from discord import app_commands
import os
from ollama import AsyncClient
from ollama import Client

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)

messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
]

for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
  print(part['message']['content'], end='', flush=True)


class AICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Inicjalizujemy asynchronicznego klienta pobierając klucz i adres chmury z .env
        self.ai_client = AsyncClient(
            host=os.getenv("OLLAMA_HOST", "https://api.ollama.com"),
        )
        # Oficjalny globalny model chmurowy akceptowany przez api.ollama.com
        self.model_name = "gemma4:31b"

    @app_commands.command(name="ai", description="Ask a question to the official Ollama Cloud AI model")
    async def ask_ai(self, interaction: discord.Interaction, prompt: str):
        # 1. Informujemy Discorda, że bot myśli, aby uniknąć błędu "zepsutej aplikacji"
        await interaction.response.defer(ephemeral=False)

        try:
            # 2. Wysyłamy asynchroniczne zapytanie do oficjalnej chmury Ollamy
            response = await self.ai_client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    }
                ]
            )

            # 3. Wyciągamy wygenerowaną odpowiedź z formatu JSON
            ai_response = response['message']['content']

            # 4. Sprawdzamy limit znaków wiadomości na Discordzie (max 2000)
            if len(ai_response) > 1900:
                ai_response = ai_response[:1900] + "\n\n*(Response trimmed due to Discord character limits)*"

            # 5. Wysyłamy gotową odpowiedź na serwer
            await interaction.followup.send(f"🤖 **Question from {interaction.user.mention}:** {prompt}\n\n{ai_response}")

        except Exception as e:
            print(f"Ollama Cloud API Error: {e}")
            await interaction.followup.send(
                "❌ An error occurred while connecting to Ollama Cloud. Please verify the API key configuration.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AICog(bot))
