import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands


# =========================================================
# RENDER HTTP SERVER
# =========================================================

class HealthCheck(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass


def run_web_server():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthCheck
    )

    print(f"🌐 HTTP server running on port {port}")

    server.serve_forever()


threading.Thread(
    target=run_web_server,
    daemon=True
).start()


# =========================================================
# DISCORD INTENTS
# =========================================================

intents = discord.Intents.default()

intents.members = True
intents.message_content = True


# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# CHANNEL ID
# =========================================================

# Kênh phỏng vấn / khảo sát
SURVEY_CHANNEL_ID = 1516067915772989541

# Kênh Verify
VERIFY_CHANNEL_ID = 1524035172193013971


# =========================================================
# ROLE ID - LEVEL
# =========================================================

LEVEL_ROLES = {

    "A": 1526550072777506987,  # Lv 1-50
    "B": 1526550215526580234,  # Lv 50-100
    "C": 1526550423408738446,  # Lv 100-200
    "D": 1526550541411553310,  # Lv 200-300
    "E": 1526550629529423942   # Lv 300+
}


# =========================================================
# ROLE ID - TRÌNH ĐỘ
# =========================================================

SKILL_ROLES = {

    "A": 1515539967047241869,  # Newbie
    "B": 1515892846912081951,  # Tập sự
    "C": 1525158742507655210,  # Pro
    "D": 1525545106642309120   # Master
}


# =========================================================
# LƯU CÂU TRẢ LỜI
# =========================================================

user_answers = {}


# =========================================================
# NHẬN MESSAGE
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    print(
        f"📩 MESSAGE: "
        f"{message.author}: "
        f"{message.content}"
    )

    await bot.process_commands(message)


# =========================================================
# KIỂM TRA NGƯỜI BẤM NÚT
# =========================================================

async def check_user(
    interaction,
    member_id
):

    if interaction.user.id != member_id:

        await interaction.response.send_message(
            "❌ Đây không phải khảo sát của bạn!",
            ephemeral=True
        )

        return False

    return True


# =========================================================
# CÂU 1 - LEVEL
# =========================================================

class LevelView(discord.ui.View):

    def __init__(self, member_id):

        super().__init__(timeout=600)

        self.member_id = member_id


    async def choose_level(
        self,
        interaction,
        answer
    ):

        if not await check_user(
            interaction,
            self.member_id
        ):
            return


        member = interaction.guild.get_member(
            self.member_id
        )

        if member is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy thành viên!",
                ephemeral=True
            )

            return


        role = interaction.guild.get_role(
            LEVEL_ROLES[answer]
        )

        if role is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy role!",
                ephemeral=True
            )

            return


        # Xóa role level cũ

        for role_id in LEVEL_ROLES.values():

            old_role = interaction.guild.get_role(
                role_id
            )

            if old_role and old_role in member.roles:

                try:
                    await member.remove_roles(
                        old_role
                    )

                except discord.Forbidden:
                    pass


        # Cấp role mới

        try:

            await member.add_roles(
                role
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Bot không có quyền cấp role này!",
                ephemeral=True
            )

            return


        # Lưu câu trả lời

        user_answers.setdefault(
            self.member_id,
            {}
        )

        user_answers[
            self.member_id
        ]["level"] = answer


        print(
            f"✅ {member} chọn level {answer}"
        )


        await interaction.response.send_message(
            f"✅ Đã chọn **{role.name}**!",
            ephemeral=True
        )


    @discord.ui.button(
        label="A",
        style=discord.ButtonStyle.primary
    )
    async def a(self, interaction, button):

        await self.choose_level(
            interaction,
            "A"
        )


    @discord.ui.button(
        label="B",
        style=discord.ButtonStyle.primary
    )
    async def b(self, interaction, button):

        await self.choose_level(
            interaction,
            "B"
        )


    @discord.ui.button(
        label="C",
        style=discord.ButtonStyle.primary
    )
    async def c(self, interaction, button):

        await self.choose_level(
            interaction,
            "C"
        )


    @discord.ui.button(
        label="D",
        style=discord.ButtonStyle.primary
    )
    async def d(self, interaction, button):

        await self.choose_level(
            interaction,
            "D"
        )


    @discord.ui.button(
        label="E",
        style=discord.ButtonStyle.primary
    )
    async def e(self, interaction, button):

        await self.choose_level(
            interaction,
            "E"
        )


# =========================================================
# CÂU 2 - TRÌNH ĐỘ
# =========================================================

class SkillView(discord.ui.View):

    def __init__(self, member_id):

        super().__init__(timeout=600)

        self.member_id = member_id


    async def choose_skill(
        self,
        interaction,
        answer
    ):

        if not await check_user(
            interaction,
            self.member_id
        ):
            return


        member = interaction.guild.get_member(
            self.member_id
        )

        if member is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy thành viên!",
                ephemeral=True
            )

            return


        role = interaction.guild.get_role(
            SKILL_ROLES[answer]
        )

        if role is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy role!",
                ephemeral=True
            )

            return


        # Xóa role trình độ cũ

        for role_id in SKILL_ROLES.values():

            old_role = interaction.guild.get_role(
                role_id
            )

            if old_role and old_role in member.roles:

                try:
                    await member.remove_roles(
                        old_role
                    )

                except discord.Forbidden:
                    pass


        # Cấp role mới

        try:

            await member.add_roles(
                role
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Bot không có quyền cấp role này!",
                ephemeral=True
            )

            return


        # Lưu câu trả lời

        user_answers.setdefault(
            self.member_id,
            {}
        )

        user_answers[
            self.member_id
        ]["skill"] = answer


        print(
            f"🎉 {member} hoàn thành khảo sát!"
        )


        # Chỉ người vừa trả lời thấy

        await interaction.response.send_message(

            f"🎉 **Bạn đã hoàn thành khảo sát!**\n\n"
            f"👉 Hãy qua <#{VERIFY_CHANNEL_ID}> "
            f"để xác minh và mở khóa "
            f"các kênh và tính năng.",

            ephemeral=True
        )


    @discord.ui.button(
        label="A",
        style=discord.ButtonStyle.success
    )
    async def a(self, interaction, button):

        await self.choose_skill(
            interaction,
            "A"
        )


    @discord.ui.button(
        label="B",
        style=discord.ButtonStyle.success
    )
    async def b(self, interaction, button):

        await self.choose_skill(
            interaction,
            "B"
        )


    @discord.ui.button(
        label="C",
        style=discord.ButtonStyle.success
    )
    async def c(self, interaction, button):

        await self.choose_skill(
            interaction,
            "C"
        )


    @discord.ui.button(
        label="D",
        style=discord.ButtonStyle.success
    )
    async def d(self, interaction, button):

        await self.choose_skill(
            interaction,
            "D"
        )


# =========================================================
# GỬI KHẢO SÁT
# =========================================================

async def send_survey(member):

    channel = member.guild.get_channel(
        SURVEY_CHANNEL_ID
    )

    if channel is None:

        print(
            "❌ Không tìm thấy kênh khảo sát!"
        )

        return


    user_answers[
        member.id
    ] = {}


    print(
        f"📋 Gửi khảo sát cho {member}"
    )


    # =====================================================
    # CÂU 1
    # =====================================================

    embed1 = discord.Embed(

        title="📋 KHẢO SÁT THÀNH VIÊN MỚI",

        description=(

            f"👋 Xin chào {member.mention}!\n"
            "Hãy trả lời khảo sát để nhận role 👾\n\n"

            "📝 **Hướng dẫn:**\n"
            "• Chọn đáp án bằng nút bên dưới.\n"
            "• Chỉ bạn mới có thể trả lời.\n\n"

            "### 1️⃣ Level hiện tại của bạn?\n\n"

            "A. Lv 1–50\n"
            "B. Lv 50–100\n"
            "C. Lv 100–200\n"
            "D. Lv 200–300\n"
            "E. Lv 300+\n\n"

            "👇 **Chọn đáp án bên dưới**"
        )
    )


    await channel.send(

        content=member.mention,

        embed=embed1,

        view=LevelView(
            member.id
        )
    )


    # =====================================================
    # CÂU 2
    # =====================================================

    embed2 = discord.Embed(

        title="2️⃣ BẠN TỰ NHẬN MÌNH LÀ?",

        description=(

            "A. Newbie\n"
            "B. Tập sự\n"
            "C. Pro\n"
            "D. Master\n\n"

            "👇 **Chọn đáp án bên dưới**"
        )
    )


    await channel.send(

        content=member.mention,

        embed=embed2,

        view=SkillView(
            member.id
        )
    )


    print(
        f"✅ Đã gửi khảo sát cho {member}"
    )


# =========================================================
# TỰ ĐỘNG KHI MEMBER JOIN
# =========================================================

@bot.event
async def on_member_join(member):

    print(
        f"👋 Thành viên mới: "
        f"{member} ({member.id})"
    )

    try:

        await send_survey(
            member
        )

    except Exception as error:

        print(
            f"❌ Lỗi gửi khảo sát: {error}"
        )


# =========================================================
# !SURVEY
# =========================================================

@bot.command()
@commands.has_permissions(
    administrator=True
)
async def survey(ctx):

    print(
        f"🧪 !survey bởi {ctx.author}"
    )

    try:

        await send_survey(
            ctx.author
        )

    except Exception as error:

        print(
            f"❌ Lỗi !survey: {error}"
        )

        await ctx.send(
            "❌ Có lỗi khi gửi khảo sát. "
            "Kiểm tra Render Logs."
        )


# =========================================================
# LỖI COMMAND
# =========================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        print(
            f"⚠️ Command không tồn tại: "
            f"{ctx.message.content}"
        )

        return


    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "❌ Bạn cần quyền Administrator "
            "để dùng lệnh này."
        )

        return


    print(
        f"❌ COMMAND ERROR: {error}"
    )


# =========================================================
# BOT READY
# =========================================================

@bot.event
async def on_ready():

    print(
        "================================="
    )

    print(
        f"🤖 BOT ONLINE: {bot.user}"
    )

    print(
        f"🆔 BOT ID: {bot.user.id}"
    )

    print(
        "================================="
    )


# =========================================================
# TOKEN
# =========================================================

token = os.environ.get(
    "DISCORD_TOKEN"
)

if not token:

    raise RuntimeError(
        "❌ DISCORD_TOKEN chưa được cài!"
    )


# =========================================================
# START
# =========================================================

print(
    "🚀 Starting Discord bot..."
)

bot.run(
    token
    )
