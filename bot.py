import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents)

# ===== GLOBAL =====
AUTOMOD_ENABLED = False
AFK_USERS = {}
LOGGING = False
LOG_CHANNEL_ID = None

# ===== CUSTOM EMOJIS (EDIT IDs) =====
TICK = "<a:tick:123456789>"
CROSS = "<a:cross:123456789>"
LOADING = "<a:loading:123456789>"
SHIELD = "<a:shield:123456789>"

FOOTER = "Firewall X Security™"

# ===== READY =====
@bot.event
async def on_ready():
    print(f"🔥 Logged in as {bot.user}")

# ===== AUTOMOD PANEL =====
@bot.group()
@commands.has_permissions(administrator=True)
async def automod(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title=f"{SHIELD} AUTOMOD PANEL",
            description="```yaml\nAdvanced Protection System\n```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Enable", value="`&automod enable`")
        embed.add_field(name="Disable", value="`&automod disable`")
        embed.add_field(name="Logging", value="`&automod logging`")
        embed.set_footer(text=FOOTER)
        await ctx.send(embed=embed)

@automod.command()
async def enable(ctx):
    global AUTOMOD_ENABLED
    AUTOMOD_ENABLED = True

    embed = discord.Embed(
        description="```diff\n+ Automod Enabled\n```",
        color=discord.Color.green()
    )
    embed.set_footer(text=FOOTER)
    embed.timestamp = ctx.message.created_at

    await ctx.send(f"{TICK}", embed=embed)

@automod.command()
async def disable(ctx):
    global AUTOMOD_ENABLED
    AUTOMOD_ENABLED = False

    embed = discord.Embed(
        description="```diff\n- Automod Disabled\n```",
        color=discord.Color.red()
    )
    embed.set_footer(text=FOOTER)
    embed.timestamp = ctx.message.created_at

    await ctx.send(f"{CROSS}", embed=embed)

@automod.command()
async def logging(ctx):
    global LOGGING
    LOGGING = not LOGGING

    embed = discord.Embed(
        description=f"```yaml\nLogging: {'Enabled' if LOGGING else 'Disabled'}\n```",
        color=discord.Color.orange()
    )
    embed.set_footer(text=FOOTER)

    await ctx.send(f"{LOADING}", embed=embed)

# ===== SET LOG CHANNEL =====
@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id

    embed = discord.Embed(
        description=f"```diff\n+ Log channel set to {channel.name}\n```",
        color=discord.Color.green()
    )
    embed.set_footer(text=FOOTER)

    await ctx.send(f"{TICK}", embed=embed)

# ===== AFK =====
@bot.command()
async def afk(ctx, *, reason="AFK"):
    AFK_USERS[ctx.author.id] = reason

    embed = discord.Embed(
        description=f"😴 {ctx.author.mention} is now AFK\nReason: {reason}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=FOOTER)
    embed.timestamp = ctx.message.created_at

    await ctx.send(f"{LOADING}", embed=embed)

# ===== MODERATION =====
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)

    embed = discord.Embed(
        description=f"👢 {member.mention} kicked\nReason: {reason}",
        color=discord.Color.red()
    )
    embed.set_footer(text=FOOTER)

    await ctx.send(f"{TICK}", embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)

    embed = discord.Embed(
        description=f"🔨 {member.mention} banned\nReason: {reason}",
        color=discord.Color.dark_red()
    )
    embed.set_footer(text=FOOTER)

    await ctx.send(f"{TICK}", embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)

    embed = discord.Embed(
        description=f"🧹 Cleared {amount} messages",
        color=discord.Color.orange()
    )
    embed.set_footer(text=FOOTER)

    await ctx.send(embed=embed, delete_after=3)

# ===== ON MESSAGE =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # AFK REMOVE
    if message.author.id in AFK_USERS:
        del AFK_USERS[message.author.id]
        embed = discord.Embed(
            description=f"👋 Welcome back {message.author.mention}, AFK removed",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)

    # AFK MENTION
    for user_id, reason in AFK_USERS.items():
        if f"<@{user_id}>" in message.content:
            embed = discord.Embed(
                description=f"😴 <@{user_id}> is AFK\nReason: {reason}",
                color=discord.Color.blue()
            )
            await message.channel.send(embed=embed)

    # AUTOMOD
    if AUTOMOD_ENABLED:

        # BAD WORD
        bad_words = ["bc", "mc", "gali"]
        if any(word in message.content.lower() for word in bad_words):
            await message.delete()
            embed = discord.Embed(
                description=f"{CROSS} {message.author.mention} Bad word not allowed",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)

        # ANTI LINK
        if "http" in message.content:
            await message.delete()
            embed = discord.Embed(
                description=f"{CROSS} {message.author.mention} Links not allowed",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)

        # LOGGING
        if LOGGING and LOG_CHANNEL_ID:
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="📜 Message Log",
                    description=f"{message.author}: {message.content}",
                    color=discord.Color.orange()
                )
                await log_channel.send(embed=embed)

    await bot.process_commands(message)

# ===== RUN =====
bot.run("YOUR_BOT_TOKEN")