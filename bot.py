import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands


class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheck)
    server.serve_forever()


threading.Thread(target=run_web_server, daemon=True).start()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập: {bot.user}")


@bot.command()
async def test(ctx):
    await ctx.send("Bot đang hoạt động! 😎")


token = os.environ.get("DISCORD_TOKEN")

if not token:
    raise RuntimeError("Không tìm thấy DISCORD_TOKEN!")

bot.run(token)
