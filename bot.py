import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập: {bot.user}")

token = os.getenv("DISCORD_TOKEN")

print("Có nhận được token:", bool(token))
print("Độ dài token:", len(token) if token else 0)

bot.run(token)
