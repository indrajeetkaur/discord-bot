import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents, help_command=None)

# ===== READY =====
@bot.event
async def on_ready():
    print(f"{bot.user} online ho gaya!")

# ===== EMBED =====
def get_main_embed():
    embed = discord.Embed(
        title="🔥 Firewall X Help Menu",
        description="Use dropdown & button below",
        color=discord.Color.red()
    )

    embed.add_field(
        name="📌 Main Modules:",
        value="""
🛡️ Antinuke Security  
🔒 Anti Betray ⭐  
⏱️ Limit System ⭐  
🚨 Auto Emergency ⭐  
⚠️ Emergency  
🔧 Moderation  
🛠️ Utility  
🤖 Automod  
👋 Welcoming  
🎨 Customroles  
🎉 Giveaway ⭐  
🚫 Boycott/VcBan 🔥  
⚙️ Automations  
😂 Fun  
🎤 Voice  
🧰 Admin / Mod Setup  
❌ Ignore Commands  
""",
        inline=False
    )

    embed.set_footer(text="Select a module from dropdown 👇")
    return embed

# ===== DROPDOWN =====
class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Antinuke", emoji="🛡️"),
            discord.SelectOption(label="Moderation", emoji="🔧"),
            discord.SelectOption(label="Fun", emoji="😂"),
            discord.SelectOption(label="Utility", emoji="🛠️"),
            discord.SelectOption(label="Automod", emoji="🤖"),
            discord.SelectOption(label="Giveaway", emoji="🎉"),
        ]
        super().__init__(placeholder="Choose a Module", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]

        if selected == "Moderation":
            msg = "🔧 **Moderation Commands**\n&ban\n&kick\n&mute\n&warn"
        elif selected == "Fun":
            msg = "😂 **Fun Commands**\n&meme\n&joke\n&avatar"
        elif selected == "Utility":
            msg = "🛠️ **Utility Commands**\n&ping\n&userinfo\n&serverinfo"
        elif selected == "Antinuke":
            msg = "🛡️ **Antinuke System**\nSetup logs, anti-ban, anti-kick"
        elif selected == "Automod":
            msg = "🤖 **Automod Commands**\nSpam filter\nLink filter"
        elif selected == "Giveaway":
            msg = "🎉 **Giveaway Commands**\n&gstart\n&gend\n&greroll"
        else:
            msg = "Coming soon..."

        await interaction.response.send_message(msg, ephemeral=True)

# ===== VIEW =====
class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

# ===== HELP COMMAND =====
@bot.command()
async def help(ctx):
    await ctx.send(embed=get_main_embed(), view=HelpView())

# ===== BASIC COMMANDS =====
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

# ===== RUN =====
bot.run(os.getenv("BOT_TOKEN"))
