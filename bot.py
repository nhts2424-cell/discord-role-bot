import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands


# =========================================================
# RENDER HEALTH CHECK
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
    server = HTTPServer(("0.0.0.0", port), HealthCheck)
    server.serve_forever()


threading.Thread(
    target=run_web_server,
    daemon=True
).start()


# =========================================================
# DISCORD
# =========================================================

intents = discord.Intents.default()

# Cho phép bot nhận thông tin thành viên mới
intents.members = True

# Cho phép bot đọc tin nhắn
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# CẤU HÌNH
# =========================================================

# ID KÊNH KHẢO SÁT
SURVEY_CHANNEL_ID = 0

# ID KÊNH VERIFY
VERIFY_CHANNEL_ID = 1524035172193013971


# =========================================================
# ROLE LEVEL
# =========================================================

LEVEL_ROLES = {

    "A": 1526550072777506987,  # Lv 1-50
    "B": 1526550215526580234,  # Lv 50-100
    "C": 1526550423408738446,  # Lv 100-200
    "D": 1526550541411553310,  # Lv 200-300
    "E": 1526550629529423942   # Lv 300+
}


# =========================================================
# ROLE TRÌNH ĐỘ
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
# KIỂM TRA NGƯỜI BẤM NÚT
# =========================================================

async def check_user(interaction, member_id):

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


    async def choose_level(self, interaction, answer):

        if not await check_user(
            interaction,
            self.member_id
        ):
            return

        member = interaction.guild.get_member(
            self.member_id
        )

        if member is None:
            return

        role_id = LEVEL_ROLES[answer]

        role = interaction.guild.get_role(
            role_id
        )

        if role is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy role.",
                ephemeral=True
            )

            return


        # Xóa role level cũ

        for old_role_id in LEVEL_ROLES.values():

            old_role = interaction.guild.get_role(
                old_role_id
            )

            if old_role and old_role in member.roles:

                try:
                    await member.remove_roles(
                        old_role
                    )
                except:
                    pass


        # Thêm role mới

        try:

            await member.add_roles(role)

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Bot không có quyền cấp role này.",
                ephemeral=True
            )

            return


        # Lưu câu trả lời

        if self.member_id not in user_answers:

            user_answers[self.member_id] = {}

        user_answers[self.member_id]["level"] = answer


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


    async def choose_skill(self, interaction, answer):

        if not await check_user(
            interaction,
            self.member_id
        ):
            return

        member = interaction.guild.get_member(
            self.member_id
        )

        if member is None:
            return

        role_id = SKILL_ROLES[answer]

        role = interaction.guild.get_role(
            role_id
        )

        if role is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy role.",
                ephemeral=True
            )

            return


        # Xóa role trình độ cũ

        for old_role_id in SKILL_ROLES.values():

            old_role = interaction.guild.get_role(
                old_role_id
            )

            if old_role and old_role in member.roles:

                try:
                    await member.remove_roles(
                        old_role
                    )
                except:
                    pass


        # Thêm role mới

        try:

            await member.add_roles(role)

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Bot không có quyền cấp role này.",
                ephemeral=True
            )

            return


        # Lưu câu trả lời

        if self.member_id not in user_answers:

            user_answers[self.member_id] = {}

        user_answers[self.member_id]["skill"] = answer


        await interaction.response.send_message(
            f"✅ Đã chọn **{role.name}**!",
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
# TỰ ĐỘNG GỬI KHẢO SÁT KHI CÓ NGƯỜI MỚI
# =========================================================

@bot.event
async def on_member_join(member):

    if SURVEY_CHANNEL_ID == 1516067915772989541:

        print(
            "Chưa đặt SURVEY_CHANNEL_ID!"
        )

        return


    channel = member.guild.get_channel(
        SURVEY_CHANNEL_ID
    )

    if channel is None:

        print(
            "Không tìm thấy kênh khảo sát!"
        )

        return


    # Khởi tạo dữ liệu

    user_answers[member.id] = {}


    # =====================================================
    # TIN NHẮN KHẢO SÁT
    # =====================================================

    embed = discord.Embed(

        title="📋 KHẢO SÁT THÀNH VIÊN MỚI",

        description=(

            f"👋 XIN CHÀO {member.mention} "
            "BÂY GIỜ HÃY TRẢ LỜI KHẢO SÁT "
            "ĐỂ LẤY ROLE 👾\n\n"

            "📝 **Hướng dẫn:**\n"
            "• Mỗi câu chỉ chọn 1 đáp án.\n"
            "• Bấm nút bên dưới để chọn.\n"
            "• Bạn chỉ có thể trả lời khảo sát của mình.\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "### 1️⃣ Level hiện tại của bạn?\n\n"

            "A. Lv 1–50\n"
            "B. Lv 50–100\n"
            "C. Lv 100–200\n"
            "D. Lv 200–300\n"
            "E. Lv 300+\n\n"

            "👇 **Bấm nút bên dưới để chọn**"
        )
    )


    await channel.send(
        content=member.mention,
        embed=embed,
        view=LevelView(member.id)
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

            "👇 **Bấm nút bên dưới để chọn**"
        )
    )


    await channel.send(
        content=member.mention,
        embed=embed2,
        view=SkillView(member.id)
    )


    # =====================================================
    # THÔNG BÁO VERIFY
    # =====================================================

    verify_channel = member.guild.get_channel(
        VERIFY_CHANNEL_ID
    )

    if verify_channel:

        await verify_channel.send(

            f"📌 {member.mention} "
            "sau khi hoàn thành khảo sát, "
            "hãy qua đây để **xác minh và mở khóa "
            "các kênh và tính năng**!"
        )


# =========================================================
# BOT READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"Bot đã đăng nhập: {bot.user}"
    )


# =========================================================
# TOKEN
# =========================================================

token = os.environ.get(
    "DISCORD_TOKEN"
)

if not token:

    raise RuntimeError(
        "Không tìm thấy DISCORD_TOKEN!"
    )


bot.run(token)
