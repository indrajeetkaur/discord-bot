import discord
from discord.ext import commands
import tim
from collections import defaultdict
import re

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents)

bot.tree = discord.app_commands.CommandTree(bot)

JOINS = defaultdict(list)

AFK = {}
SPAM = defaultdict(list)
LOG_CHANNEL = None

AFK = {}
SPAM = defaultdict(list)
LOG_CHANNEL = None

BAD_WORDS = ["mc", "bc", "madarchod", "bhosdike"]

ALLOWED_ROLES = []

MUTE_ROLE = None

LINK_REGEX = r"(https?://\S+|www\.\S+)"

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

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verify Me", style=discord.ButtonStyle.green)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if VERIFY_ROLE is None:
            await interaction.response.send_message("❌ Verify role not set", ephemeral=True)
            return

        role = interaction.guild.get_role(VERIFY_ROLE)

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            embed=em(
                "✅ VERIFIED",
                f"➤ User :: {interaction.user.mention}\n➤ Status :: Verified Successfully",
                discord.Color.green()
            ),
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
@commands.has_permissions(administrator=True)
async def verifypanel(ctx):
    await ctx.send(
        embed=em(
            "🛡️ SERVER VERIFICATION",
            "➤ Click the button below to verify yourself\n➤ Get access to the server",
            discord.Color.blurple()
        ),
        view=VerifyView()
    )

@bot.command()
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL
    LOG_CHANNEL = channel.id
    await ctx.send(embed=em("📜 LOG SYSTEM ENABLED", f"🛡️ Channel: {channel.mention}\n✅ Status: Active", discord.Color.green()))

# ===== MOD COMMANDS =====
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban()

    await ctx.send(embed=em(
        "🔨 USER BANNED",
        f"➤ User      :: {member.mention}\n➤ Reason    :: {reason}\n➤ Action    :: Permanent Ban",
        discord.Color.red()
    ))

    await log(ctx.guild, em(
        "📜 BAN LOG",
        f"➤ Moderator :: {ctx.author.mention}\n➤ User      :: {member}\n➤ Reason    :: {reason}",
        discord.Color.red()
    ))

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick()

    await ctx.send(embed=em(
        "👢 USER KICKED",
        f"➤ User      :: {member.mention}\n➤ Reason    :: {reason}\n➤ Action    :: Removed",
        discord.Color.orange()
    ))

    await log(ctx.guild, em(
        "📜 KICK LOG",
        f"➤ Moderator :: {ctx.author.mention}\n➤ User      :: {member}\n➤ Reason    :: {reason}",
        discord.Color.orange()
    ))

VERIFY_ROLE = None

@bot.command()
@commands.has_permissions(administrator=True)
async def setverify(ctx, role: discord.Role):
    global VERIFY_ROLE
    VERIFY_ROLE = role.id
    await ctx.send("✅ Verify role set")

@bot.command()
async def verify(ctx):
    if VERIFY_ROLE:
        role = ctx.guild.get_role(VERIFY_ROLE)
        await ctx.author.add_roles(role)
        await ctx.send(embed=em(
            "✅ VERIFIED",
            f"{ctx.author.mention} is now verified",
            discord.Color.green()
        ))

@bot.command()
@commands.has_permissions(administrator=True)
async def allowlink(ctx, role: discord.Role):
    if role.id not in ALLOWED_ROLES:
        ALLOWED_ROLES.append(role.id)

    await ctx.send(embed=em(
        "✅ LINK PERMISSION ADDED",
        f"➤ Role :: {role.mention}\n➤ Status :: Can send links",
        discord.Color.green()
    ))

@bot.command()
@commands.has_permissions(administrator=True)
async def setmute(ctx, role: discord.Role):
    global MUTE_ROLE
    MUTE_ROLE = role.id
    await ctx.send("✅ Mute role set")

# SPAM DETECT ke niche add kar 👇
if len(SPAM[m.author.id]) > 5:
    role = m.guild.get_role(MUTE_ROLE)
    if role:
        await m.author.add_roles(role)

    await m.channel.send(embed=em(
        "🚫 AUTO MUTE",
        f"🛡️ {m.author.mention}\n⚠️ Spamming detected\n🔇 Muted",
        discord.Color.red()
    ))

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    WARNS[member.id] += 1
    count = WARNS[member.id]

    await ctx.send(embed=em(
        "⚠️ USER WARNED",
        f"➤ User      :: {member.mention}\n➤ Reason    :: {reason}\n➤ Total     :: {count}",
        discord.Color.orange()
    ))

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
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)

    await ctx.send(embed=em(
        "🗑️ CHAT CLEARED",
        f"➤ Deleted   :: {amount} messages\n➤ Channel   :: {ctx.channel.mention}",
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
        f"➤ User      :: {ctx.author.mention}\n➤ Reason    :: {reason}",
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
    if m.author.bot:
        return

    # 👻 GHOST PING DETECT
    if m.mentions:
        await m.channel.send(embed=em(
            "👻 GHOST PING DETECTED",
            f"🛡️ {m.author.mention}\n⚠️ Deleted a message with mentions",
            discord.Color.red()
        ))

    # 📜 LOG DELETE (PRO EMBED)
    await log(m.guild, em(
        "📜 MESSAGE DELETED",
        f"👤 User :: {m.author.mention}\n"
        f"📍 Channel :: {m.channel.mention}\n"
        f"🗑️ Content :: {m.content if m.content else 'No text'}",
        discord.Color.red()
    ))

@bot.event
async def on_message_edit(before, after):
    await log(before.guild, em("📜 MESSAGE EDIT", f"✏️ {before.content} ➜ {after.content}", discord.Color.orange()))

@bot.event
async def on_ready():
    await bot.tree.sync()          # slash commands ke liye
    bot.add_view(VerifyView())     # verify button ke liye

    print(f"🔥 {bot.user} ONLINE")

@bot.event
async def on_member_update(before, after):
    if any(word in after.display_name.lower() for word in BAD_WORDS):
        await after.edit(nick="🚫 Bad Name")

        await log(after.guild, em(
            "⚠️ BAD NICKNAME",
            f"🛡️ {after.mention} nickname changed",
            discord.Color.orange()
        ))

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
   if re.search(LINK_REGEX, m.content):
    
    # ✅ ROLE BYPASS
    if any(role.id in ALLOWED_ROLES for role in m.author.roles):
        return

        await m.delete()

        await m.channel.send(embed=em(
            "❌ LINK BLOCKED",
            f"➤ User :: {m.author.mention}\n➤ Action :: Message Removed\n➤ Reason :: Links not allowed",
            discord.Color.red()
        ))

        return 

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