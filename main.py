import discord
from discord.ext import commands
from keep_alive import keep_alive
import asyncio
import os

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True  # Required for reading user messages

bot = commands.Bot(command_prefix="c!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def main():
    # Load cogs here inside the async function
    await bot.load_extension("character")
    await bot.load_extension("conscious")
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

# Run the bot
keep_alive()
if __name__ == "__main__":
    asyncio.run(main())
