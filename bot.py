
import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os
import asyncio
import time

AUTOMOD_ENABLED = False
AUTOMOD_LOGGING = True
AUTOMOD_PUNISHMENT = "warn"  # warn / mute / kick / ban

IGNORE_CHANNELS = set()
IGNORE_ROLES = set() 

afk_users = {}

LIMIT_ENABLED = True
LIMIT_COUNT = 3
LIMIT_LOGGING = True

AUTO_EMERGENCY = False
EMERGENCY_TRIGGERED = False
user_actions = {}
EMERGENCY_LOG_CHANNEL = None

EMERGENCY_ENABLED = False
EMERGENCY_ROLES = set()
EMERGENCY_AUTH = set()

whitelist = set()
extra_owners = set()
ANTINUKE_ENABLED = False
LOG_CHANNEL = None

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

    # ✅ Emergency trigger
    if message.mention_everyone:
        await handle_emergency(message.guild, message.author, "everyone")

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
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL
    LOG_CHANNEL = channel.id
    await ctx.send(f"✅ Log channel set to {channel.mention}")

bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason

    embed = discord.Embed(
        description=f"😴 {ctx.author.mention} is now AFK: {reason}",
        color=discord.Color.yellow()
    )
    await ctx.send(embed=embed)

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(
        title="🤖 BOT INFO",
        color=discord.Color.blue()
    )
    embed.add_field(name="Name", value=bot.user.name)
    embed.add_field(name="Servers", value=len(bot.guilds))
    embed.add_field(name="Users", value=len(bot.users))
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=embed)
@bot.command()
async def channelinfo(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel

    embed = discord.Embed(
        title="📺 CHANNEL INFO",
        color=discord.Color.blue()
    )

    embed.add_field(name="Name", value=channel.name)
    embed.add_field(name="ID", value=channel.id)
    embed.add_field(name="Category", value=channel.category)

    await ctx.send(embed=embed)

@bot.command()
async def permissions(ctx, member: discord.Member = None):
    member = member or ctx.author

    perms = [perm[0] for perm in member.guild_permissions if perm[1]]

    embed = discord.Embed(
        title="🔐 PERMISSIONS",
        description="\n".join(perms),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

@bot.group()
async def list(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Use: bots / admins / roles / emojis")

@list.command()
async def bots(ctx):
    bots = [m.mention for m in ctx.guild.members if m.bot]

    embed = discord.Embed(
        title="🤖 BOT LIST",
        description="\n".join(bots)[:4000],
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@list.command()
async def admins(ctx):
    admins = [m.mention for m in ctx.guild.members if m.guild_permissions.administrator]

    embed = discord.Embed(
        title="👑 ADMIN LIST",
        description="\n".join(admins)[:4000],
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

@list.command()
async def roles(ctx):
    roles = [r.name for r in ctx.guild.roles]

    embed = discord.Embed(
        title="🎭 ROLE LIST",
        description="\n".join(roles)[:4000],
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

@list.command()
async def emojis(ctx):
    emojis = [str(e) for e in ctx.guild.emojis]

    embed = discord.Embed(
        title="😀 EMOJI LIST",
        description=" ".join(emojis)[:4000],
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

@list.command(name="inrole")
async def inrole(ctx, role: discord.Role):
    members = [m.mention for m in role.members]

    embed = discord.Embed(
        title=f"👥 Members in {role.name}",
        description="\n".join(members)[:4000],
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx):
    embed = discord.Embed(
        title="📊 BOT STATS",
        color=discord.Color.green()
    )
    embed.add_field(name="Guilds", value=len(bot.guilds))
    embed.add_field(name="Users", value=len(bot.users))
    embed.add_field(name="Latency", value=f"{round(bot.latency*1000)}ms")
    await ctx.send(embed=embed)

@bot.command()
async def roleinfo(ctx, role: discord.Role):
    embed = discord.Embed(
        title="🎭 ROLE INFO",
        color=role.color
    )

    embed.add_field(name="Name", value=role.name)
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Members", value=len(role.members))
    embed.add_field(name="Color", value=str(role.color))

    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    embed = discord.Embed(
        title="🔗 INVITE ME",
        description="[Click Here](https://discord.com/oauth2/authorize?client_id=YOUR_ID&permissions=8&scope=bot)",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title="👤 USER INFO",
        color=discord.Color.purple()
    )
    embed.add_field(name="Name", value=member)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%d %b %Y"))
    embed.set_thumbnail(url=member.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title="🏠 SERVER INFO",
        color=discord.Color.orange()
    )
    embed.add_field(name="Name", value=guild.name)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=guild.owner)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.blue()
    )
    embed.set_image(url=member.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def timer(ctx, seconds: int):
    embed = discord.Embed(
        title="⏱️ TIMER STARTED",
        description=f"{seconds} seconds",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

    await asyncio.sleep(seconds)

    await ctx.send(f"⏰ {ctx.author.mention} Timer ended!")

@bot.command()
async def membercount(ctx):
    embed = discord.Embed(
        title="👥 MEMBER COUNT",
        description=f"{ctx.guild.member_count} members",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(
        title="📊 POLL",
        description=question,
        color=discord.Color.gold()
    )

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


# ===== ANTINUKE VIEW =====
class AntinukeView(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.green)
    async def proceed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("✅ Antinuke Confirmed", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()


# ===== ANTINUKE COMMAND =====
@bot.group()
@commands.has_permissions(administrator=True)
async def antinuke(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f"⚙️ Antinuke is {'ENABLED' if ANTINUKE_ENABLED else 'DISABLED'}")


# ===== ENABLE =====
@antinuke.command()
async def enable(ctx):
    global ANTINUKE_ENABLED
    ANTINUKE_ENABLED = True

    embed = discord.Embed(
        title="🚨 Antinuke System Enabled",
        description=(
            "• Protection Activated Successfully\n"
            "• Server is now secured from attacks\n"
            "• All dangerous actions will be monitored\n\n"
            "⚡ Stay Safe & Protected"
        ),
        color=discord.Color.red()
    )

    embed.set_footer(text="Firewall X Security™")

    await ctx.send(embed=embed, view=AntinukeView())


# ===== DISABLE =====
@antinuke.command()
async def disable(ctx):
    global ANTINUKE_ENABLED
    ANTINUKE_ENABLED = False

    embed = discord.Embed(
        title="❌ Antinuke System Disabled",
        description=(
            "• Protection Disabled\n"
            "• Server is now vulnerable ⚠️\n\n"
            "⚡ Enable it again to stay safe"
        ),
        color=discord.Color.dark_red()
    )

    embed.set_footer(text="Firewall X Security™")

    await ctx.send(embed=embed, view=AntinukeView())

# ===== EXTRA OWNER =====
@bot.group()
@commands.has_permissions(administrator=True)
async def extraowner(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Use set/view/reset")

@extraowner.command()
async def set(ctx, member: discord.Member):
    if member.id in extra_owners:
        return await ctx.send("⚠️ User is already an extra owner.")

    extra_owners.add(member.id)

    embed = discord.Embed(
        title="👑 Extra Owner Added",
        description=f"{member.mention} has been successfully granted extra owner privileges.",
        color=discord.Color.gold()
    )

    embed.add_field(name="User", value=f"{member}", inline=True)
    embed.add_field(name="Action By", value=f"{ctx.author.mention}", inline=True)

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


@extraowner.command()
async def view(ctx):
    if not extra_owners:
        embed = discord.Embed(
            title="📂 Extra Owners",
            description="No extra owners have been set.",
            color=discord.Color.orange()
        )
        return await ctx.send(embed=embed)

    users = "\n".join([f"<@{uid}>" for uid in extra_owners])

    embed = discord.Embed(
        title="📂 Extra Owners List",
        description=users,
        color=discord.Color.blue()
    )

    embed.add_field(name="Total", value=str(len(extra_owners)), inline=True)

    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


@extraowner.command()
async def reset(ctx):
    if not extra_owners:
        return await ctx.send("⚠️ No extra owners to reset.")

    extra_owners.clear()

    embed = discord.Embed(
        title="♻️ Extra Owners Reset",
        description="All extra owners have been successfully removed.",
        color=discord.Color.red()
    )

    embed.add_field(name="Action By", value=f"{ctx.author.mention}", inline=True)

    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)

# ===== LIMIT SYSTEM =====
@bot.group()
@commands.has_permissions(administrator=True)
async def limit(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="⚙️ LIMIT CONTROL PANEL",
            description=(
                "```yaml\n"
                "Manage server protection limits easily\n"
                "Use commands below 👇\n"
                "```"
            ),
            color=discord.Color.dark_blue()
        )

        embed.add_field(
            name="🟢 Enable",
            value="`&limit enable`",
            inline=True
        )

        embed.add_field(
            name="🔴 Disable",
            value="`&limit disable`",
            inline=True
        )

        embed.add_field(
            name="⚙️ Set Limit",
            value="`&limit set <number>`",
            inline=True
        )

        embed.add_field(
            name="📊 Settings",
            value="`&limit settings`",
            inline=True
        )

        embed.add_field(
            name="📢 Logging",
            value="`&limit logging`",
            inline=True
        )

        embed.set_footer(text="Firewall X Security™ • Limit System")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

        await ctx.send(embed=embed)


# ===== ENABLE =====
@limit.command()
async def enable(ctx):
    global LIMIT_ENABLED
    LIMIT_ENABLED = True

    embed = discord.Embed(
        title="🟢 LIMIT ENABLED",
        description="```diff\n+ Protection limit system is now ACTIVE\n```",
        color=discord.Color.green()
    )

    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


# ===== DISABLE =====
@limit.command()
async def disable(ctx):
    global LIMIT_ENABLED
    LIMIT_ENABLED = False

    embed = discord.Embed(
        title="🔴 LIMIT DISABLED",
        description="```diff\n- Protection limit system is now OFF\n```",
        color=discord.Color.red()
    )

    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


# ===== SET LIMIT =====
@limit.command()
async def set(ctx, number: int):
    global LIMIT_COUNT
    LIMIT_COUNT = number

    embed = discord.Embed(
        title="⚙️ LIMIT UPDATED",
        description=f"```yaml\nNew Limit: {number}\n```",
        color=discord.Color.blurple()
    )

    embed.add_field(name="Changed By", value=ctx.author.mention)
    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


# ===== SETTINGS =====
@limit.command()
async def settings(ctx):
    embed = discord.Embed(
        title="📊 CURRENT LIMIT SETTINGS",
        description="```ini\nSystem Configuration Overview\n```",
        color=discord.Color.dark_green()
    )

    embed.add_field(
        name="🟢 Status",
        value=f"`{'ENABLED' if LIMIT_ENABLED else 'DISABLED'}`",
        inline=True
    )

    embed.add_field(
        name="⚙️ Limit",
        value=f"`{LIMIT_COUNT}` actions",
        inline=True
    )

    embed.add_field(
        name="📢 Logging",
        value=f"`{'ON' if LIMIT_LOGGING else 'OFF'}`",
        inline=True
    )

    embed.set_footer(text="Firewall X Security™ • Live Stats")
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


# ===== LOGGING TOGGLE =====
@limit.command()
async def logging(ctx):
    global LIMIT_LOGGING
    LIMIT_LOGGING = not LIMIT_LOGGING

    embed = discord.Embed(
        title="📢 LOGGING TOGGLED",
        description=f"```yaml\nLogging: {'Enabled' if LIMIT_LOGGING else 'Disabled'}\n```",
        color=discord.Color.orange()
    )

    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)


@bot.group()
@commands.has_permissions(administrator=True)
async def automod(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🛡️ AUTOMOD PANEL",
            description="```yaml\nAdvanced Moderation System\n```",
            color=discord.Color.blurple()
        )

        embed.add_field(name="Enable", value="`&automod enable`")
        embed.add_field(name="Disable", value="`&automod disable`")
        embed.add_field(name="Punishment", value="`&automod punishment <type>`")
        embed.add_field(name="Logging", value="`&automod logging`")

        embed.add_field(name="Ignore", value="`&automod ignore channel/role`")
        embed.add_field(name="Unignore", value="`&automod unignore channel/role`")

        await ctx.send(embed=embed)

# ✅ ENABLE
@automod.command()
async def enable(ctx):
    global AUTOMOD_ENABLED
    AUTOMOD_ENABLED = True

    await ctx.send(embed=discord.Embed(
        description="```diff\n+ Automod Enabled\n```",
        color=discord.Color.green()
    ))

@automod.command()
async def disable(ctx):
    global AUTOMOD_ENABLED
    AUTOMOD_ENABLED = False

    await ctx.send(embed=discord.Embed(
        description="```diff\n- Automod Disabled\n```",
        color=discord.Color.red()
    ))

# ===== AUTO EMERGENCY =====
@bot.group(name="auto")
@commands.has_permissions(administrator=True)
async def auto(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🚨 AUTO EMERGENCY PANEL",
            description="```yaml\nAdvanced Server Protection System\n```",
            color=discord.Color.dark_red()
        )

        embed.add_field(name="🟢 Enable", value="`&auto emergency enable`", inline=True)
        embed.add_field(name="🔴 Disable", value="`&auto emergency disable`", inline=True)
        embed.add_field(name="♻️ Restore", value="`&auto emergency restore`", inline=True)

        await ctx.send(embed=embed)


@auto.group(name="emergency", aliases=["emg"])
async def emergency(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Use: enable / disable / restore")

# ===== ENABLE =====
@emergency.command()
async def enable(ctx):
    global AUTO_EMERGENCY
    AUTO_EMERGENCY = True

    embed = discord.Embed(
        title="🟢 AUTO EMERGENCY ENABLED",
        description="```diff\n+ Emergency system is now ACTIVE\n```",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# ===== DISABLE =====
@emergency.command()
async def disable(ctx):
    global AUTO_EMERGENCY
    AUTO_EMERGENCY = False

    embed = discord.Embed(
        title="🔴 AUTO EMERGENCY DISABLED",
        description="```diff\n- Emergency system is now OFF\n```",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)


# ===== RESTORE =====
@emergency.command()
@commands.is_owner()
async def restore(ctx):
    global EMERGENCY_TRIGGERED

    if not EMERGENCY_TRIGGERED:
        return await ctx.send("⚠️ No emergency actions to restore.")

    EMERGENCY_TRIGGERED = False

    embed = discord.Embed(
        title="♻️ SERVER RESTORED",
        description="```yaml\nAll permissions restored successfully\n```",
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed)

@bot.group()
@commands.has_permissions(manage_messages=True)
async def clear(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🧹 CLEAR PANEL",
            description="```yaml\nUse: all / bots / user\n```",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)


@clear.command()
async def all(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

    embed = discord.Embed(
        title="🧹 MESSAGES CLEARED",
        description=f"```diff\n- Deleted {amount} messages\n```",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, delete_after=3)


@clear.command()
async def bots(ctx, amount: int):
    await ctx.channel.purge(limit=amount, check=lambda m: m.author.bot)

    embed = discord.Embed(
        title="🤖 BOT MESSAGES CLEARED",
        description=f"Deleted {amount} bot messages",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed, delete_after=3)


@clear.command()
async def user(ctx, member: discord.Member, amount: int):
    await ctx.channel.purge(limit=amount, check=lambda m: m.author == member)

    embed = discord.Embed(
        title="👤 USER MESSAGES CLEARED",
        description=f"Deleted {amount} messages from {member.mention}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, delete_after=3)

# ===== WHITELIST =====
@bot.command()
async def wl(ctx, member: discord.Member):
    whitelist.add(member.id)
    
    embed = discord.Embed(
        title="✅ User Whitelisted",
        description=f"{member.mention} has been successfully added to the whitelist.",
        color=discord.Color.green()
    )

    embed.add_field(name="User", value=f"{member}", inline=True)
    embed.add_field(name="Action By", value=f"{ctx.author.mention}", inline=True)

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at
    
    await ctx.send(embed=embed)


@bot.command()
async def unwl(ctx, member: discord.Member):
    whitelist.discard(member.id)
    
    embed = discord.Embed(
        title="❌ User Removed from Whitelist",
        description=f"{member.mention} has been successfully removed from the whitelist.",
        color=discord.Color.red()
    )
    
    embed.add_field(name="User", value=f"{member}", inline=True)
    embed.add_field(name="Action By", value=f"{ctx.author.mention}", inline=True)
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Firewall X Security™")
    embed.timestamp = ctx.message.created_at
    
    await ctx.send(embed=embed)

@bot.command()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

    embed = discord.Embed(
        title="🔒 CHANNEL LOCKED",
        description=f"{ctx.channel.mention} has been locked",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

    embed = discord.Embed(
        title="🔓 CHANNEL UNLOCKED",
        description=f"{ctx.channel.mention} has been unlocked",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)

    embed = discord.Embed(
        title="✅ USER UNBANNED",
        description=f"{user} has been unbanned",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)

    embed = discord.Embed(
        title="🐢 SLOWMODE ENABLED",
        description=f"Slowmode set to {seconds}s",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)


@bot.command()
async def unslowmode(ctx):
    await ctx.channel.edit(slowmode_delay=0)

    embed = discord.Embed(
        title="⚡ SLOWMODE DISABLED",
        description="Slowmode removed",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def hide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)

    embed = discord.Embed(
        title="🙈 CHANNEL HIDDEN",
        description=f"{ctx.channel.mention} is now hidden",
        color=discord.Color.dark_grey()
    )
    await ctx.send(embed=embed)


@bot.command()
async def unhide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True)

    embed = discord.Embed(
        title="👀 CHANNEL VISIBLE",
        description=f"{ctx.channel.mention} is now visible",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def nuke(ctx):
    new = await ctx.channel.clone()
    await ctx.channel.delete()

    embed = discord.Embed(
        title="💥 CHANNEL NUKED",
        description=f"{new.mention} recreated successfully",
        color=discord.Color.red()
    )
    await new.send(embed=embed)

@bot.command()
async def clone(ctx):
    new = await ctx.channel.clone()

    embed = discord.Embed(
        title="📋 CHANNEL CLONED",
        description=f"Created: {new.mention}",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
async def reminder(ctx, seconds: int, *, msg):
    embed = discord.Embed(
        title="⏰ Reminder Set",
        description=f"{msg}\nTime: {seconds}s",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    await asyncio.sleep(seconds)

    await ctx.send(f"🔔 {ctx.author.mention} Reminder: {msg}")

@bot.command()
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author

    user = await bot.fetch_user(member.id)

    if user.banner:
        embed = discord.Embed(
            title=f"{member.name}'s Banner",
            color=discord.Color.purple()
        )
        embed.set_image(url=user.banner.url)
    else:
        embed = discord.Embed(
            description="❌ No banner found",
            color=discord.Color.red()
        )

    await ctx.send(embed=embed) 

@bot.command()
async def badges(ctx, member: discord.Member = None):
    member = member or ctx.author

    flags = member.public_flags

    badges = [flag.name for flag in flags.all()]

    embed = discord.Embed(
        title="🎭 BADGES",
        description="\n".join(badges) if badges else "No badges",
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

import hashlib

@bot.command()
async def hash(ctx, *, text):
    hashed = hashlib.md5(text.encode()).hexdigest()

    embed = discord.Embed(
        title="🔐 HASH",
        description=f"`{hashed}`",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

@bot.command()
async def rickroll(ctx, member: discord.Member):
    embed = discord.Embed(
        title="😈 GOTCHA!",
        description=f"{member.mention} you got rickrolled!",
        color=discord.Color.red()
    )

    embed.add_field(name="Video", value="https://youtu.be/dQw4w9WgXcQ")

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def secure(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, use_external_apps=False)

    embed = discord.Embed(
        title="🔐 SERVER SECURED",
        description="```diff\n- External Apps Disabled In All Channels\n```",
        color=discord.Color.dark_red()
    )

    embed.set_footer(text="Firewall X Security™")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)

    # Executor (moderator)
    executor = ctx.author

    embed = discord.Embed(
        description=f"🔨 Successfully Banned {member}",
        color=discord.Color.red()
    )

    embed.add_field(name="Target User", value=f"{member}", inline=False)
    embed.add_field(name="Mention", value=f"{member.mention}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=f"{executor.mention}", inline=False)
    embed.add_field(name="DM Sent", value="No", inline=False)

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=f"Requested by {executor} | Today")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)

 # ✅ LOG PART
    if LOG_CHANNEL:
        log_channel = bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)

    embed = discord.Embed(
        description=f"👢 Successfully Kicked {member}",
        color=discord.Color.orange()
    )

    embed.add_field(name="Target User", value=f"{member}", inline=False)
    embed.add_field(name="Mention", value=f"{member.mention}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
    embed.add_field(name="DM Sent", value="No", inline=False)

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author} | Today")
    embed.timestamp = ctx.message.created_at

    await ctx.send(embed=embed)

    # 🔥 LOG SYSTEM
    if LOG_CHANNEL:
        log_channel = bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)

# ===== ERROR HANDLER =====

@ban.error
async def ban_error(ctx, error):
    await ctx.send("❌ Permission nahi hai ya galat use")

@kick.error
async def kick_error(ctx, error):
    await ctx.send("❌ Permission nahi hai ya galat use")

async def punish(member):
    try:
        await member.ban(reason="Antinuke 🚨")

        if LOG_CHANNEL:
            log = bot.get_channel(LOG_CHANNEL)
            if log:
                embed = discord.Embed(
                    description=f"🚨 User punished",
                    color=discord.Color.red()
                )
                embed.add_field(name="User", value=f"{member}")
                embed.add_field(name="Action", value="Ban")
                await log.send(embed=embed)

    except:
        pass

# ===== ANTINUKE =====
LIMIT = 3
TIME = 10

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

async def handle_emergency(guild, user, action):
    global EMERGENCY_TRIGGERED

    if not AUTO_EMERGENCY:
        return

    user_id = user.id
    now = time.time()

    if user_id not in user_actions:
        user_actions[user_id] = []

    user_actions[user_id] = [t for t in user_actions[user_id] if now - t < 600]
    user_actions[user_id].append(now)

    if len(user_actions[user_id]) >= 40 and not EMERGENCY_TRIGGERED:
        EMERGENCY_TRIGGERED = True

        # 🚨 ACTION: BAN USER
        member = guild.get_member(user_id)
        if member:
            try:
                await member.ban(reason="🚨 Emergency Mode Triggered")
            except:
                pass

        # 🔒 LOCK SERVER (basic)
        for role in guild.roles:
            try:
                await role.edit(permissions=discord.Permissions.none())
            except:
                continue

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

        if executor.id == 1410852730427277374:
            return

        if not ANTINUKE_ENABLED:
            return

        if executor.id in whitelist:
            return

        if executor.id in extra_owners:
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

    # ✅ EMERGENCY
    await handle_emergency(guild, member, "kick")

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if executor.id == 1410852730427277374:
            return

        if not ANTINUKE_ENABLED:
            return

        if executor.id in whitelist:
            return

        if executor.id in extra_owners:
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

        if executor.id == 1410852730427277374:
            return

        if not ANTINUKE_ENABLED:
            return

        if executor.id in whitelist:
            return

        if executor.id in extra_owners:
            return

        if check_user(executor.id):
            await punish(executor)

# ===== BAN =====
@bot.event
async def on_member_ban(guild, user):
    await asyncio.sleep(1)

    # ✅ EMERGENCY CALL
    await handle_emergency(guild, user, "ban")

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        executor = entry.user

        if executor.bot or executor == guild.owner:
            return

        if executor.id == 1410852730427277374:
            return

        if not ANTINUKE_ENABLED:
            return

        if executor.id in whitelist:
            return

        if executor.id in extra_owners:
            return

        if check_user(executor.id):
            await punish(executor) 

        channel = guild.system_channel  # ya apna log channel id daal

        if channel:
            embed = discord.Embed(
                description=f"🔨 Successfully Banned {user}",
                color=discord.Color.red()
            )

            embed.add_field(name="Target User", value=f"{user}", inline=False)
            embed.add_field(name="Mention", value=f"<@{user.id}>", inline=False)
            embed.add_field(name="Moderator", value=f"{executor.mention}", inline=False)
            embed.add_field(name="Reason", value="No reason provided", inline=False)

            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Action by {executor}")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"👋 Welcome back {message.author.mention}, AFK removed.")

    for user_id, reason in afk_users.items():
        if f"<@{user_id}>" in message.content:
            await message.channel.send(f"😴 <@{user_id}> is AFK: {reason}")

    await bot.process_commands(message)

# ===== RUN =====
bot.run(os.getenv("BOT_TOKEN"))
