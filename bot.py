import os
import sqlite3
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands


# =========================================================
# RENDER WEB SERVER
# =========================================================

class HealthCheck(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Discord Role Bot is running!")

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

SURVEY_CHANNEL_ID = 1516067915772989541

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
# DATABASE
# =========================================================

DATABASE_FILE = "survey.db"


db = sqlite3.connect(
    DATABASE_FILE,
    check_same_thread=False
)

db_lock = threading.Lock()


def setup_database():

    with db_lock:

        db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        db.commit()


setup_database()


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_status(
    guild_id,
    user_id
):

    with db_lock:

        result = db.execute(
            """
            SELECT status
            FROM members
            WHERE guild_id = ?
            AND user_id = ?
            """,
            (
                guild_id,
                user_id
            )
        ).fetchone()

    if result is None:
        return None

    return result[0]


def set_status(
    guild_id,
    user_id,
    status
):

    with db_lock:

        db.execute(
            """
            INSERT INTO members
                (guild_id, user_id, status)
            VALUES
                (?, ?, ?)

            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET
                status = excluded.status
            """,
            (
                guild_id,
                user_id,
                status
            )
        )

        db.commit()


def member_is_known(
    guild_id,
    user_id
):

    with db_lock:

        result = db.execute(
            """
            SELECT 1
            FROM members
            WHERE guild_id = ?
            AND user_id = ?
            """,
            (
                guild_id,
                user_id
            )
        ).fetchone()

    return result is not None


# =========================================================
# USER ANSWERS
# =========================================================

user_answers = {}


# =========================================================
# CHECK USER
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
# LEVEL BUTTONS
# =========================================================

class LevelView(discord.ui.View):

    def __init__(
        self,
        member_id
    ):

        super().__init__(
            timeout=None
        )

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
                "❌ Không tìm thấy role Level!",
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

                    print(
                        f"❌ Không thể xóa role "
                        f"{old_role.name}"
                    )


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
            f"✅ {member} chọn Level {answer}"
        )


        await interaction.response.send_message(
            f"✅ Đã nhận **{role.name}**!\n"
            "➡️ Bây giờ hãy trả lời câu 2.",
            ephemeral=True
        )


    @discord.ui.button(
        label="A",
        style=discord.ButtonStyle.primary,
        custom_id="survey_level_A"
    )
    async def button_a(
        self,
        interaction,
        button
    ):

        await self.choose_level(
            interaction,
            "A"
        )


    @discord.ui.button(
        label="B",
        style=discord.ButtonStyle.primary,
        custom_id="survey_level_B"
    )
    async def button_b(
        self,
        interaction,
        button
    ):

        await self.choose_level(
            interaction,
            "B"
        )


    @discord.ui.button(
        label="C",
        style=discord.ButtonStyle.primary,
        custom_id="survey_level_C"
    )
    async def button_c(
        self,
        interaction,
        button
    ):

        await self.choose_level(
            interaction,
            "C"
        )


    @discord.ui.button(
        label="D",
        style=discord.ButtonStyle.primary,
        custom_id="survey_level_D"
    )
    async def button_d(
        self,
        interaction,
        button
    ):

        await self.choose_level(
            interaction,
            "D"
        )


    @discord.ui.button(
        label="E",
        style=discord.ButtonStyle.primary,
        custom_id="survey_level_E"
    )
    async def button_e(
        self,
        interaction,
        button
    ):

        await self.choose_level(
            interaction,
            "E"
        )


# =========================================================
# SKILL BUTTONS
# =========================================================

class SkillView(discord.ui.View):

    def __init__(
        self,
        member_id
    ):

        super().__init__(
            timeout=None
        )

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
                "❌ Không tìm thấy role trình độ!",
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

                    print(
                        f"❌ Không thể xóa role "
                        f"{old_role.name}"
                    )


        # Cấp role

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


        # Đánh dấu hoàn thành

        set_status(
            interaction.guild.id,
            self.member_id,
            "completed"
        )


        print(
            f"🎉 {member} đã hoàn thành khảo sát!"
        )


        # Chỉ người trả lời thấy

        await interaction.response.send_message(

            f"🎉 **Bạn đã hoàn thành khảo sát!**\n\n"
            f"👉 Hãy qua <#{VERIFY_CHANNEL_ID}> "
            f"để xác minh và mở khóa "
            f"các kênh và tính năng.",

            ephemeral=True
        )


    @discord.ui.button(
        label="A",
        style=discord.ButtonStyle.success,
        custom_id="survey_skill_A"
    )
    async def button_a(
        self,
        interaction,
        button
    ):

        await self.choose_skill(
            interaction,
            "A"
        )


    @discord.ui.button(
        label="B",
        style=discord.ButtonStyle.success,
        custom_id="survey_skill_B"
    )
    async def button_b(
        self,
        interaction,
        button
    ):

        await self.choose_skill(
            interaction,
            "B"
        )


    @discord.ui.button(
        label="C",
        style=discord.ButtonStyle.success,
        custom_id="survey_skill_C"
    )
    async def button_c(
        self,
        interaction,
        button
    ):

        await self.choose_skill(
            interaction,
            "C"
        )


    @discord.ui.button(
        label="D",
        style=discord.ButtonStyle.success,
        custom_id="survey_skill_D"
    )
    async def button_d(
        self,
        interaction,
        button
    ):

        await self.choose_skill(
            interaction,
            "D"
        )


# =========================================================
# GỬI KHẢO SÁT
# =========================================================

async def send_survey(
    member
):

    if member.bot:
        return


    guild_id = member.guild.id

    user_id = member.id


    # Nếu đã hoàn thành thì không gửi

    status = get_status(
        guild_id,
        user_id
    )


    if status == "completed":

        print(
            f"⏭️ Bỏ qua {member} "
            "(đã hoàn thành)"
        )

        return


    channel = member.guild.get_channel(
        SURVEY_CHANNEL_ID
    )


    if channel is None:

        print(
            f"❌ Không tìm thấy kênh "
            f"{SURVEY_CHANNEL_ID}"
        )

        return


    # Đánh dấu pending

    set_status(
        guild_id,
        user_id,
        "pending"
    )


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

            "📝 **Gợi ý:**\n"
            "Bấm trực tiếp vào nút A, B, C, D hoặc E "
            "bên dưới để chọn đáp án.\n\n"

            "### 1️⃣ Level hiện tại của bạn là?\n\n"

            "🅰️ Lv 1–50\n"
            "🅱️ Lv 50–100\n"
            "🇨 Lv 100–200\n"
            "🇩 Lv 200–300\n"
            "🇪 Lv 300+\n\n"

            "👇 **Bấm nút bên dưới để chọn**"
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

            "🅰️ Newbie\n"
            "🅱️ Tập sự\n"
            "🇨 Pro\n"
            "🇩 Master\n\n"

            "💡 **Gợi ý:** Chọn mức phù hợp nhất "
            "với kinh nghiệm của bạn.\n\n"

            "👇 **Bấm nút bên dưới để chọn**"
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
# NGƯỜI MỚI VÀO SERVER
# =========================================================

@bot.event
async def on_member_join(
    member
):

    if member.bot:
        return


    print(
        f"👋 MEMBER JOIN: "
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
# KHI BOT ONLINE
# =========================================================

@bot.event
async def on_ready():

    print(
        "===================================="
    )

    print(
        f"🤖 BOT ONLINE: {bot.user}"
    )

    print(
        f"🆔 BOT ID: {bot.user.id}"
    )

    print(
        "===================================="
    )


    # Đăng ký persistent views
    # để nút vẫn hoạt động sau restart

    bot.add_view(
        LevelView(0)
    )

    bot.add_view(
        SkillView(0)
    )


    # =====================================================
    # PHÁT HIỆN THÀNH VIÊN VÀO KHI BOT OFF
    # =====================================================

    for guild in bot.guilds:

        print(
            f"🔎 Kiểm tra server: {guild.name}"
        )


        current_members = set()


        for member in guild.members:

            if member.bot:
                continue


            current_members.add(
                member.id
            )


            known = member_is_known(
                guild.id,
                member.id
            )


            if not known:

                # Người này chưa từng được bot ghi nhận.
                # Có thể là người vào khi bot OFF,
                # hoặc người đã ở server trước khi bot cài.

                print(
                    f"🆕 Phát hiện thành viên "
                    f"chưa được ghi nhận: {member}"
                )


                await send_survey(
                    member
                )


    print(
        "✅ Hoàn tất kiểm tra thành viên."
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
# !PING
# =========================================================

@bot.command()
async def ping(ctx):

    await ctx.send(
        "🏓 Pong!"
    )


# =========================================================
# COMMAND ERROR
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
# TOKEN
# =========================================================

token = os.environ.get(
    "DISCORD_TOKEN"
)


if not token:

    raise RuntimeError(
        "❌ Không tìm thấy DISCORD_TOKEN!"
    )


# =========================================================
# START BOT
# =========================================================

print(
    "🚀 Starting Discord bot..."
)


bot.run(
    token
)
