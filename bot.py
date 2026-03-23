import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os
import asyncio

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

# ===== ANTINUKE SYSTEM (FIXED) =====

import time

user_actions = {}
LIMIT = 3
TIME = 10  # seconds

async def punish(member):
    try:
        await member.ban(reason="Antinuke Protection 🚨")
    except:
        pass

def check_user(user_id):
    current_time = time.time()

    if user_id not in user_actions:
        user_actions[user_id] = []

    # purane actions hatao
    user_actions[user_id] = [
        t for t in user_actions[user_id]
        if current_time - t < TIME
    ]

    user_actions[user_id].append(current_time)

    return len(user_actions[user_id]) >= LIMIT

# ===== BAN PROTECTION =====
@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if check_user(executor.id):
            await punish(executor)

# ===== KICK PROTECTION =====
@bot.event
async def on_member_remove(member):
    guild = member.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if check_user(executor.id):
            await punish(executor)

# ===== CHANNEL DELETE =====
===== BASIC COMMANDS =====
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

# ===== ANTINUKE SYSTEM (FIXED) =====

import time

user_actions = {}
LIMIT = 3
TIME = 10  # seconds

async def punish(member):
    try:
        await member.ban(reason="Antinuke Protection 🚨")
    except:
        pass

def check_user(user_id):
    current_time = time.time()

    if user_id not in user_actions:
        user_actions[user_id] = []

    # purane actions hatao
    user_actions[user_id] = [
        t for t in user_actions[user_id]
        if current_time - t < TIME
    ]

    user_actions[user_id].append(current_time)

    return len(user_actions[user_id]) >= LIMIT

# ===== BAN PROTECTION =====
@bot.event
async def on_member_ban(guild, user):
    await asyncio.sleep(1)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if check_user(executor.id):
            await punish(executor) 

 ===== KICK PROTECTION =====
@bot.event
async def on_member_remove(member):
    guild = member.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if check_user(executor.id):
            await punish(executor)

# ===== CHANNEL DELETE =====
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if check_user(executor.id):
            await punish(executor)

# ===== RUN =====
bot.run(os.getenv("BOT_TOKEN"))
