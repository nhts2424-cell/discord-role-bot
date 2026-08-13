import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Đã đăng nhập: {bot.user}")

token = os.environ.get("DISCORD_TOKEN")

if token is None:
    raise RuntimeError("KHÔNG TÌM THẤY DISCORD_TOKEN")

bot.run(token)
