
import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os
import asyncio
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents, help_command=None)

# ===== READY =====
@bot.event
async def on_ready():
    print(f"{bot.user} online ho gaya!")

# ===== DEBUG (IMPORTANT) =====
@bot.event
async def on_message(message):
    print(message.content)
    await bot.process_commands(message)

# ===== EMBED =====
def get_main_embed():
    embed = discord.Embed(
        title="🔥 Firewall X Help Menu",
        description="Use dropdown & button below",
        color=discord.Color.red()
    )
    embed.add_field(
        name="📌 Main Modules:",
        value="🛡️ Antinuke\n🔧 Moderation\n😂 Fun\n🛠️ Utility",
        inline=False
    )
    return embed

# ===== DROPDOWN =====
class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Antinuke", emoji="🛡️"),
            discord.SelectOption(label="Moderation", emoji="🔧"),
            discord.SelectOption(label="Fun", emoji="😂"),
            discord.SelectOption(label="Utility", emoji="🛠️"),
        ]
        super().__init__(placeholder="Choose Module", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Working ✅", ephemeral=True)

# ===== VIEW =====
class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

# ===== HELP =====
@bot.command()
async def help(ctx):
    await ctx.send(embed=get_main_embed(), view=HelpView())

# ===== PING =====
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")
# ===== MODERATION COMMANDS =====

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked!")

# ===== ERROR HANDLER =====

@ban.error
async def ban_error(ctx, error):
    await ctx.send("❌ Permission nahi hai ya galat use")

@kick.error
async def kick_error(ctx, error):
    await ctx.send("❌ Permission nahi hai ya galat use")

# ===== ANTINUKE =====
user_actions = {}
LIMIT = 3
TIME = 10

async def punish(member):
    try:
        await member.ban(reason="Antinuke 🚨")
    except:
        pass

def check_user(user_id):
    current_time = time.time()
    if user_id not in user_actions:
        user_actions[user_id] = []

    user_actions[user_id] = [
        t for t in user_actions[user_id]
        if current_time - t < TIME
    ]

    user_actions[user_id].append(current_time)
    return len(user_actions[user_id]) >= LIMIT

# ===== ANTI BETRAY SYSTEM =====

DANGEROUS_PERMS = [
    "administrator",
    "manage_guild",
    "ban_members",
    "kick_members",
    "manage_roles"
]

@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return

    guild = after.guild
    await asyncio.sleep(1)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if executor.id ==1410852730427277374
            return

        added_roles = [role for role in after.roles if role not in before.roles]

        for role in added_roles:
            for perm in DANGEROUS_PERMS:
                if getattr(role.permissions, perm):
                    try:
                        await after.remove_roles(role)
                        await punish(executor)
                    except:
                        pass

# ===== KICK =====
@bot.event
async def on_member_remove(member):
    guild = member.guild
    await asyncio.sleep(1)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if executor.id ==1410852730427277374
            return

        if check_user(executor.id):
            await punish(executor)

# ===== CHANNEL DELETE =====
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    await asyncio.sleep(1)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if executor.id ==1410852730427277374
            return

        if check_user(executor.id):
            await punish(executor)

# ===== BAN =====
@bot.event
async def on_member_ban(guild, user):
    await asyncio.sleep(1)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if executor.id ==1410852730427277374
            return

        if check_user(executor.id):
            await punish(executor)

# ===== RUN =====
bot.run(os.getenv("BOT_TOKEN"))