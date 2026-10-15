import asyncio
import threading
import socket
import platform
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import discord
from discord import app_commands
from discord.ext import commands

# ----------------- CẤU HÌNH BẢO MẬT -----------------
# Token sẽ được GitHub Actions tự động nhét vào khi build qua biến môi trường
DISCORD_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "DEFAULT_TOKEN")
GUILD_ID = 1559935255790616738             # ID Server Discord của sếp

def get_device_info():
    hostname = socket.gethostname().lower()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "127.0.0.1"
    
    os_info = f"Android ({platform.machine()})"
    return {
        "hostname": f"android-{hostname}",
        "os": os_info,
        "ip": ip
    }

DEV_INFO = get_device_info()
DEVICE_NAME = DEV_INFO["hostname"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
target_channel = None

@bot.event
async def on_ready():
    global target_channel
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    channel_name = DEVICE_NAME.replace(" ", "-")
    target_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not target_channel:
        try:
            target_channel = await guild.create_text_channel(name=channel_name)
        except Exception:
            return

    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    except Exception:
        pass

    startup_msg = (
        f"📱 **ĐIỆN THOẠI ANDROID ĐÃ KẾT NỐI DISCORD**\n"
        f"📲 Tên thiết bị: `{DEVICE_NAME}`\n"
        f"🤖 Hệ điều hành: `{DEV_INFO['os']}`\n"
        f"🌐 Địa chỉ IP: `{DEV_INFO['ip']}`\n"
        f"🟢 Trạng thái: *Đang chạy ngầm ổn định.*"
    )
    await target_channel.send(startup_msg)

@bot.tree.command(name="ping", description="Kiểm tra phản hồi của điện thoại", guild=discord.Object(id=GUILD_ID))
async def ping_slash(interaction: discord.Interaction):
    if target_channel and interaction.channel_id == target_channel.id:
        await interaction.response.send_message(f"📱 [`{DEVICE_NAME}`] Online và sẵn sàng nhận lệnh!")
    else:
        await interaction.response.send_message("❌ Kênh này không quản lý thiết bị này!", ephemeral=True)

def start_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(DISCORD_TOKEN)

class AndroidBotApp(App):
    def build(self):
        bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
        bot_thread.start()

        layout = BoxLayout(orientation='vertical', padding=20)
        lbl = Label(
            text=f"📱 Discord Agent Android\n\nThiết bị: {DEVICE_NAME}\nTrạng thái: Đang kết nối...",
            halign="center",
            font_size='18sp'
        )
        layout.add_widget(lbl)
        return layout

if __name__ == "__main__":
    AndroidBotApp().run()
