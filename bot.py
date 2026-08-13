import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands


# =========================
# RENDER HTTP SERVER
# =========================

class HealthCheck(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass


def run_web_server():

    port = int(
        os.environ.get("PORT", 10000)
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthCheck
    )

    server.serve_forever()


threading.Thread(
    target=run_web_server,
    daemon=True
).start()


# =========================
# DISCORD INTENTS
# =========================

intents = discord.Intents.default()

intents.members = True
intents.message_content = True


# =========================
# BOT
# =========================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# NHẬN TIN NHẮN
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    print(
        f"📩 MESSAGE: {message.content}"
    )

    await bot.process_commands(
        message
    )


# =========================
# TEST COMMAND
# =========================

@bot.command()
async def ping(ctx):

    await ctx.send(
        "🏓 Pong!"
    )


# =========================
# SURVEY COMMAND
# =========================

@bot.command()
@commands.has_permissions(
    administrator=True
)
async def survey(ctx):

    print(
        f"🧪 !survey bởi {ctx.author}"
    )

    await ctx.send(
        "✅ Bot nhận được lệnh !survey!"
    )


# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():

    print(
        f"🤖 Bot Online: {bot.user}"
    )


# =========================
# TOKEN
# =========================

token = os.environ.get(
    "DISCORD_TOKEN"
)

if not token:

    raise RuntimeError(
        "❌ Không tìm thấy DISCORD_TOKEN!"
    )


bot.run(
    token
)
