import discord
from discord.ext import commands
import time
import datetime
from collections import defaultdict
import re
import os

# --- INITIALIZATION ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents)

# Global Variables
JOINS = defaultdict(list)
AFK = {}
SPAM = defaultdict(list)
WARNS = defaultdict(int) # Fixed missing WARNS
LOG_CHANNEL = None
VERIFY_ROLE = None
MUTE_ROLE = None
ALLOWED_ROLES = []
BAD_WORDS = ["mc", "bc", "madarchod", "bhosdike"]
LINK_REGEX = r"(https?://\S+|www.\S+)"

# --- EMBED STYLE FUNCTION ---
def em(title, desc, color):
    e = discord.Embed(
        title=f"✨ {title}",
        description=f"{desc}",
        color=color
    )
    e.set_footer(text="🔥 Firewall X • Ultra Security")
    e.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1828/1828640.png")
    # Note: Make sure the GIF link is valid
    e.set_image(url="https://i.imgur.com/Z6XQJZL.gif")
    e.timestamp = discord.utils.utcnow()
    return e

# --- UI VIEWS (Tickets & Verify) ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
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

    @discord.ui.button(label="✅ Verify Me", style=discord.ButtonStyle.green, custom_id="verify_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global VERIFY_ROLE
        if VERIFY_ROLE is None:
            await interaction.response.send_message("❌ Verify role not set", ephemeral=True)
            return
        
        role = interaction.guild.get_role(VERIFY_ROLE)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                embed=em("✅ VERIFIED", f"➤ User :: {interaction.user.mention}\n➤ Status :: Verified Successfully", discord.Color.green()), 
                ephemeral=True
            )

# --- BOT EVENTS ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    print(f"🔥 {bot.user} ONLINE & PROTECTING")

async def log(guild, embed):
    if LOG_CHANNEL:
        ch = guild.get_channel(LOG_CHANNEL)
        if ch: await ch.send(embed=embed)

# --- COMMANDS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def verifypanel(ctx):
    await ctx.send(embed=em("🛡️ SERVER VERIFICATION", "➤ Click the button below to verify yourself", discord.Color.blurple()), view=VerifyView())

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    await ctx.send(embed=em("🎫 SUPPORT SYSTEM", "🛡️ Click button to create ticket", discord.Color.blurple()), view=TicketView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL
    LOG_CHANNEL = channel.id
    await ctx.send(embed=em("📜 LOG SYSTEM ENABLED", f"🛡️ Channel: {channel.mention}", discord.Color.green()))

@bot.command()
@commands.has_permissions(administrator=True)
async def setverify(ctx, role: discord.Role):
    global VERIFY_ROLE
    VERIFY_ROLE = role.id
    await ctx.send(f"✅ Verify role set to {role.name}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(embed=em("🔨 USER BANNED", f"➤ User :: {member.mention}\n➤ Reason :: {reason}", discord.Color.red()))
    await log(ctx.guild, em("📜 BAN LOG", f"➤ Mod: {ctx.author}\n➤ User: {member}", discord.Color.red()))

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(embed=em("🗑️ CHAT CLEARED", f"➤ Deleted :: {amount} messages", discord.Color.orange()), delete_after=3)

# --- AUTOMOD & PROTECTION ---
@bot.event
async def on_message(m):
    if m.author.bot: return
    
    # Bypass Admin
    if m.author.guild_permissions.administrator:
        await bot.process_commands(m)
        return

    # Bad Words Filter
    if any(word in m.content.lower() for word in BAD_WORDS):
        await m.delete()
        await m.channel.send(f"⚠️ {m.author.mention}, watch your language!", delete_after=3)
        return

    # Spam Protection
    now = time.time()
    SPAM[m.author.id].append(now)
    SPAM[m.author.id] = [t for t in SPAM[m.author.id] if now - t < 5]
    
    if len(SPAM[m.author.id]) > 5:
        if MUTE_ROLE:
            role = m.guild.get_role(MUTE_ROLE)
            await m.author.add_roles(role)
            await m.channel.send(embed=em("🚫 AUTO MUTE", f"🛡️ {m.author.mention} muted for spamming", discord.Color.red()))
        else:
            await m.channel.send(f"⚠️ {m.author.mention}, stop spamming!", delete_after=2)
        return

    await bot.process_commands(m)

# --- RUN ---
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERROR: TOKEN not found in Environment Variables!")
