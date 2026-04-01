import discord
from discord.ext import commands
import time
from collections import defaultdict

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents)

JOINS = defaultdict(list)

AFK = {}
SPAM = defaultdict(list)
LOG_CHANNEL = None

AFK = {}
SPAM = defaultdict(list)
LOG_CHANNEL = None

BAD_WORDS = ["mc", "bc", "madarchod", "bhosdike"]

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction, button):
        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
        }

        ch = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )

        await interaction.response.send_message(
            embed=em("🎫 TICKET CREATED", f"🛡️ {ch.mention}", discord.Color.green()),
            ephemeral=True
        )

@bot.command()
async def ticket(ctx):
    await ctx.send(
        embed=em("🎫 SUPPORT SYSTEM", "🛡️ Click button to create ticket", discord.Color.blurple()),
        view=TicketView()
    )

# ===== EMBED STYLE =====
def em(title, desc, color):
    e = discord.Embed(
        title=f"✨ {title}",
        description=f"{desc}",
        color=color
    )
    e.set_footer(text="🔥 Firewall X • Ultra Security")
    e.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1828/1828640.png")
    e.set_image(url="https://i.imgur.com/Z6XQJZL.gif")
    e.timestamp = discord.utils.utcnow()
    return e

# ===== READY =====
@bot.event
async def on_ready():
    print(f"🔥 {bot.user} ONLINE")

# ===== LOG SYSTEM =====
async def log(guild, embed):
    if LOG_CHANNEL:
        ch = guild.get_channel(LOG_CHANNEL)
        if ch:
            await ch.send(embed=embed)

@bot.command()
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL
    LOG_CHANNEL = channel.id
    await ctx.send(embed=em("📜 LOG SYSTEM ENABLED", f"🛡️ Channel: {channel.mention}\n✅ Status: Active", discord.Color.green()))

# ===== MOD COMMANDS =====
@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban()
    await ctx.send(embed=em(
        "🔨 USER BANNED",
        f"🛡️ User: {member.mention}\n⚠️ Reason: {reason}\n🔥 Action: Permanently banned",
        discord.Color.red()
    ))
    await log(ctx.guild, em("📜 BAN LOG", f"🔨 {member} banned\n⚠️ {reason}", discord.Color.red()))

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick()
    await ctx.send(embed=em(
        "👢 USER KICKED",
        f"🛡️ User: {member.mention}\n⚠️ Reason: {reason}\n🔥 Action: Removed from server",
        discord.Color.orange()
    ))
    await log(ctx.guild, em("📜 KICK LOG", f"👢 {member} kicked\n⚠️ {reason}", discord.Color.orange()))

@bot.command()
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(embed=em(
        "♻️ USER UNBANNED",
        f"🛡️ User: {user}\n✅ Status: Restored",
        discord.Color.green()
    ))

@bot.command()
async def timeout(ctx, member: discord.Member, seconds: int):
    until = discord.utils.utcnow() + discord.timedelta(seconds=seconds)
    await member.timeout(until)
    await ctx.send(embed=em(
        "⏳ USER TIMEOUT",
        f"🛡️ User: {member.mention}\n⏳ Duration: {seconds}s\n⚠️ Action: Muted",
        discord.Color.orange()
    ))

@bot.command()
async def untimeout(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(embed=em(
        "✅ TIMEOUT REMOVED",
        f"🛡️ User: {member.mention}\n🔥 Status: Active again",
        discord.Color.green()
    ))

@bot.command()
async def clear(ctx, amount:int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(embed=em(
        "🗑️ CHAT CLEARED",
        f"🛡️ Messages Deleted: {amount}\n🔥 Cleaned successfully",
        discord.Color.orange()
    ), delete_after=3)

# ===== LOCK SYSTEM =====
@bot.command()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(embed=em(
        "🔒 CHANNEL LOCKED",
        f"🛡️ Channel: {ctx.channel.mention}\n❌ Sending messages disabled",
        discord.Color.red()
    ))

@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(embed=em(
        "🔓 CHANNEL UNLOCKED",
        f"🛡️ Channel: {ctx.channel.mention}\n✅ Sending messages enabled",
        discord.Color.green()
    ))

@bot.command()
async def reactrole(ctx, role: discord.Role):
    msg = await ctx.send(embed=em(
        "🎭 REACTION ROLE",
        f"🛡️ React to get {role.mention}\n🔥 Click below",
        discord.Color.blurple()
    ))

    await msg.add_reaction("🔥")

    def check(reaction, user):
        return reaction.message.id == msg.id and str(reaction.emoji) == "🔥"

    reaction, user = await bot.wait_for("reaction_add", check=check)
    await user.add_roles(role)

    await ctx.send(embed=em(
        "✅ ROLE GIVEN",
        f"🛡️ {user.mention} got {role.mention}",
        discord.Color.green()
    ))l

# ===== AFK =====
@bot.command()
async def afk(ctx, *, reason="AFK"):
    AFK[ctx.author.id] = reason
    await ctx.send(embed=em(
        "😴 AFK ENABLED",
        f"🛡️ User: {ctx.author.mention}\n⚠️ Reason: {reason}",
        discord.Color.blue()
    ))

# ===== EVENTS =====
@bot.event
async def on_member_join(m):
    now = time.time()
    JOINS[m.guild.id].append(now)
    JOINS[m.guild.id] = [t for t in JOINS[m.guild.id] if now - t < 10]

    # 🚨 RAID DETECT
    if len(JOINS[m.guild.id]) >= 5:
        for ch in m.guild.channels:
            await ch.set_permissions(m.guild.default_role, send_messages=False)

        await log(m.guild, em(
            "🚨 RAID DETECTED",
            "🛡️ Server auto locked due to mass join\n❌ All channels locked",
            discord.Color.red()
        ))

    if m.guild.system_channel:
        await m.guild.system_channel.send(embed=em(
            "📥 NEW MEMBER",
            f"🛡️ Welcome {m.mention}\n🔥 Stay safe!",
            discord.Color.green()
        ))

@bot.event
async def on_member_remove(m):
    await log(m.guild, em("📜 LEAVE LOG", f"📤 {m}", discord.Color.red()))

@bot.event
async def on_message_delete(m):
    await log(m.guild, em("📜 MESSAGE DELETE", f"🗑️ {m.content}", discord.Color.red()))

@bot.event
async def on_message_edit(before, after):
    await log(before.guild, em("📜 MESSAGE EDIT", f"✏️ {before.content} ➜ {after.content}", discord.Color.orange()))

# ===== MESSAGE SYSTEM =====
@bot.event
async def on_message(m):
    if m.author.bot:
        return

    if m.author.guild_permissions.administrator:
        return

 # 🤬 BAD WORD FILTER 
    if any(word in m.content.lower() for word in BAD_WORDS):
        await m.delete()
        await m.channel.send(embed=em(
            "⚠️ BAD WORD DETECTED",
            f"🛡️ {m.author.mention}\n❌ Message removed",
            discord.Color.red()
        ))
        return

    # AFK REMOVE
    if m.author.id in AFK:
        del AFK[m.author.id]
        await m.channel.send(embed=em(
            "🔥 WELCOME BACK",
            f"🛡️ {m.author.mention} is no longer AFK",
            discord.Color.green()
        ))

    # AFK MENTION
    for uid, reason in AFK.items():
        if f"<@{uid}>" in m.content:
            await m.channel.send(embed=em(
                "😴 USER AFK",
                f"🛡️ <@{uid}> is AFK\n⚠️ Reason: {reason}",
                discord.Color.blue()
            ))

    # AUTOMOD (LINK BLOCK)
    if "http" in m.content:
        await m.delete()
        await m.channel.send(embed=em(
            "❌ LINK BLOCKED",
            f"🛡️ {m.author.mention}\n⚠️ Links are not allowed",
            discord.Color.red()
        ))

    # SPAM DETECT
    now = time.time()
    SPAM[m.author.id].append(now)
    SPAM[m.author.id] = [t for t in SPAM[m.author.id] if now-t < 5]

    if len(SPAM[m.author.id]) > 5:
        await m.channel.send(embed=em(
            "🚫 SPAM DETECTED",
            f"🛡️ {m.author.mention}\n⚠️ Slow down!",
            discord.Color.red()
        ))

    await bot.process_commands(m)

# ===== RUN =====
bot.run("YOUR_BOT_TOKEN")