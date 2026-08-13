import os
import discord
from discord.ext import commands

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập: {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("Bot đang hoạt động!")

token = os.getenv("DISCORD_TOKEN")

print("TOKEN EXISTS:", token is not None)
print("TOKEN LENGTH:", len(token) if token else 0)

if not token:
    print("LỖI: Chưa có DISCORD_TOKEN trên Render!")
else:
    bot.run(token)
