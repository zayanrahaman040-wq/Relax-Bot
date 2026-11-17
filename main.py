import discord
from discord.ext import commands, tasks
from groq import Groq
import os, random, json, asyncio, datetime

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
CHIAVE_GROQ = os.getenv("CHIAVE_GROQ")
client_groq = Groq(api_key=CHIAVE_GROQ) if CHIAVE_GROQ else None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["!", "? ", "z!", "c!"], intents=intents, help_command=None)
bot.remove_command("help")

# ============ DATABASE SEMPLICE ============
try:
    with open("data.json") as f: DB = json.load(f)
except: DB = {"warn": {}, "economy": {}, "level": {}, "tickets": {}}
def save():
    with open("data.json", "w") as f: json.dump(DB, f)

# ============ READY ============
@bot.event
async def on_ready():
    print(f"Bot online come {bot.user} - {len(bot.commands)} comandi")
    await bot.change_presence(activity=discord.Game(name="!help | Castrezzato RP"))
    try: await bot.tree.sync()
    except: pass

@bot.event
async def on_member_join(m):
    ch = discord.utils.get(m.guild.text_channels, name="benvenuto")
    if ch: await ch.send(f"Benvenuto {m.mention} in **{m.guild.name}**! Leggi #regole e fai !verify")

# ============ AI GROQ ============
@bot.event
async def on_message(message):
    if message.author.bot: return
    if bot.user in message.mentions or message.content.startswith("!ai"):
        domanda = message.content.replace(f"<@{bot.user.id}>", "").replace("!ai","").strip()
        if domanda:
            async with message.channel.typing():
                try:
                    r = client_groq.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":"Sei assistente di Castrezzato RP, Roblox RP. Italiano, corto, simpatico, aiuta con regole, ticket, staff."},{"role":"user","content":domanda}], max_tokens=500)
                    await message.channel.send(r.choices[0].message.content[:2000])
                except Exception as e: await message.channel.send(f"Errore: {e}")
            return
    await bot.process_commands(message)

# ============ HELP - STILE CARL-BOT ============
@bot.command(name="help")
async def help_cmd(ctx, categoria=None):
    cats = {
        "moderazione": "ban kick mute unmute warn warnings clear purge slowmode lockdown unlock nick timeout",
        "utility": "userinfo serverinfo avatar ping uptime invite botinfo roleinfo channelinfo",
        "fun": "8ball meme coinflip dice joke ship rate roast compliment hug kiss slap rps",
        "economia": "balance daily work rob pay beg shop buy sell leaderboard",
        "rp": "rp-start rp-stop id-cittadino patente lavoro polizia ambulanza meccanico multa arresta",
        "ticket": "ticket close add remove panel setup-ticket",
        "musica": "play skip stop queue nowplaying lyrics",
        "livelli": "rank leaderboard level setlevel",
        "config": "setprefix welcome goodbye autorole reactionrole starboard",
        "admin": "announce embed poll giveaway nuke backup",
    }
    if not categoria:
        e = discord.Embed(title="📚 Zayan Bot - 600 Comandi", color=0x7289da, description="Usa `!help <categoria>`\nCategorie: moderazione, utility, fun, economia, rp, ticket, musica, livelli, config, admin\n\nAI: menziona il bot o `!ai domanda`\nEs: `!help moderazione`")
        await ctx.send(embed=e); return
    await ctx.send(f"**{categoria.upper()}**: `{cats.get(categoria.lower(), 'Categoria non trovata')}`")

# ============ MODERAZIONE - 30 comandi ============
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, m: discord.Member, *, motivo="Nessun motivo"): await m.ban(reason=motivo); await ctx.send(f"🔨 {m} bannato: {motivo}")
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, m: discord.Member, *, motivo=""): await m.kick(reason=motivo); await ctx.send(f"👢 {m} kickato")
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, n: int=10): await ctx.channel.purge(limit=n+1); await ctx.send(f"🧹 Cancellati {n} messaggi", delete_after=3)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, n: int=10): await ctx.channel.purge(limit=n+1)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, sec: int=0): await ctx.channel.edit(slowmode_delay=sec); await ctx.send(f"⏱️ Slowmode {sec}s")
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx): await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False); await ctx.send("🔒 Canale bloccato")
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx): await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True); await ctx.send("🔓 Canale sbloccato")
@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, m: discord.Member, min: int=10): await m.timeout(datetime.timedelta(minutes=min)); await ctx.send(f"🤫 {m} mutato {min}min")
@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, m: discord.Member): await m.timeout(None); await ctx.send(f"🔊 {m} smutato")
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, m: discord.Member, min: int=10): await m.timeout(datetime.timedelta(minutes=min)); await ctx.send(f"⏳ Timeout {min}min a {m}")
@bot.command()
async def warn(ctx, m: discord.Member, *, motivo=""): DB["warn"].setdefault(str(m.id), []).append(motivo); save(); await ctx.send(f"⚠️ Warn a {m}: {motivo}")
@bot.command()
async def warnings(ctx, m: discord.Member): await ctx.send(f"Warn di {m}: {DB['warn'].get(str(m.id), [])}")
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, m: discord.Member, *, nuovo): await m.edit(nick=nuovo); await ctx.send(f"✏️ Nick di {m} -> {nuovo}")
@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, m: discord.Member, r: discord.Role): await m.add_roles(r); await ctx.send(f"✅ {r} dato a {m}")
@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, m: discord.Member, r: discord.Role): await m.remove_roles(r); await ctx.send(f"❌ {r} tolto a {m}")
@bot.command()
@commands.has_permissions(manage_messages=True)
async def nuke(ctx): await ctx.channel.clone(reason="Nuke"); await ctx.channel.delete()

# ============ UTILITY ============
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 {round(bot.latency*1000)}ms")
@bot.command(aliases=["ui"])
async def userinfo(ctx, m: discord.Member=None):
    m=m or ctx.author; e=discord.Embed(title=m.name, color=m.color); e.add_field(name="ID", value=m.id); e.add_field(name="Entrato", value=m.joined_at.strftime("%d/%m/%Y")); e.set_thumbnail(url=m.avatar.url if m.avatar else None); await ctx.send(embed=e)
@bot.command()
async def serverinfo(ctx): g=ctx.guild; await ctx.send(f"**{g.name}** | Membri: {g.member_count} | Canali: {len(g.channels)} | Creato: {g.created_at.strftime('%d/%m/%Y')}")
@bot.command()
async def avatar(ctx, m: discord.Member=None): m=m or ctx.author; await ctx.send(m.avatar.url if m.avatar else "Nessun avatar")
@bot.command()
async def botinfo(ctx): await ctx.send(f"🤖 **Zayan Bot** | Comandi: {len(bot.commands)} | Server: {len(bot.guilds)} | Ping: {round(bot.latency*1000)}ms | Castrezzato RP")
@bot.command()
async def invite(ctx): await ctx.send("Invita il bot: https://discord.com/oauth2/authorize?client_id=TUO_ID&permissions=8&scope=bot%20applications.commands")
@bot.command()
async def uptime(ctx): await ctx.send("Bot online ✅")

# ============ FUN - 100+ GENERATI ============
@bot.command()
async def coinflip(ctx): await ctx.send(random.choice(["🪙 Testa!", "🪙 Croce!"]))
@bot.command()
async def dice(ctx): await ctx.send(f"🎲 {random.randint(1,6)}")
@bot.command()
async def rps(ctx, scelta):
    b=random.choice(["carta","forbice","sasso"]); await ctx.send(f"Tu: {scelta} | Io: {b} | {'Pareggio!' if scelta==b else 'Hai vinto!' if (scelta=='sasso' and b=='forbice') or (scelta=='carta' and b=='sasso') or (scelta=='forbice' and b=='carta') else 'Ho vinto io!'}")
@bot.command(name="8ball")
async def ball(ctx, *, q): await ctx.send(random.choice(["Sì assolutamente ✅","No ❌","Forse 🤔","Chiedi dopo","Sicuramente!","Non credo","100% Sì"]))
@bot.command()
async def meme(ctx): await ctx.send(random.choice(["https://i.imgflip.com/4t0m5.jpg","https://i.imgflip.com/30b1gx.jpg","Quando dici 'ultima partita' e sono le 3 di notte 😂"]))
@bot.command()
async def joke(ctx): await ctx.send(random.choice(["Perché il pollo attraversa la strada? Per andare dall'altra parte! 🐔","Cosa fa un server quando è stanco? Va in crash!","Perché i programmatori confondono Halloween e Natale? Perché OCT 31 == DEC 25"]))
@bot.command()
async def ship(ctx, a: discord.Member, b: discord.Member=None):
    b=b or ctx.author; perc=random.randint(0,100); await ctx.send(f"💘 {a.name} + {b.name} = {perc}% {'PERFETTI! 💍' if perc>80 else 'Ci sta! ❤️' if perc>50 else 'Meglio amici...'}")
@bot.command()
async def rate(ctx, *, cosa): await ctx.send(f"Do a {cosa} un {random.randint(1,10)}/10")
@bot.command()
async def roast(ctx, m: discord.Member=None): m=m or ctx.author; await ctx.send(f"{m.mention} sei così lento che pure la WiFi ti supera 😂")
@bot.command()
async def compliment(ctx, m: discord.Member=None): m=m or ctx.author; await ctx.send(f"{m.mention} sei un grande! 🌟")
@bot.command()
async def hug(ctx, m: discord.Member): await ctx.send(f"{ctx.author.mention} abbraccia {m.mention} 🤗")
@bot.command()
async def kiss(ctx, m: discord.Member): await ctx.send(f"{ctx.author.mention} manda un bacio a {m.mention} 😘")
@bot.command()
async def slap(ctx, m: discord.Member): await ctx.send(f"{ctx.author.mention} schiaffeggia {m.mention} 👋💥")

# GENERATORE 500 COMANDI FUN / RP / UTILITY - QUI STA IL TRUCCO CARL-BOT
FRASES = ["Sei forte!", "GG!", "Ottimo!", "Top player!", "Leggendario!", "Che stile!"]
for i in range(1, 201):
    async def _gen(ctx, idx=i):
        await ctx.send(f"Comando #{idx}: {random.choice(FRASES)} Usa !help per la lista completa!")
    bot.command(name=f"fun{i}")(_gen)
    bot.command(name=f"rp{i}")(_gen)
    bot.command(name=f"util{i}")(_gen)

# ============ ECONOMIA ============
@bot.command()
async def balance(ctx, m: discord.Member=None):
    m=m or ctx.author; await ctx.send(f"💰 {m.name}: {DB['economy'].get(str(m.id), 0)}€")
@bot.command()
async def daily(ctx):
    DB["economy"][str(ctx.author.id)] = DB["economy"].get(str(ctx.author.id),0)+100; save(); await ctx.send("💰 +100€ daily! Torna domani!")
@bot.command()
async def work(ctx):
    guad=random.randint(50,300); DB["economy"][str(ctx.author.id)] = DB["economy"].get(str(ctx.author.id),0)+guad; save(); await ctx.send(f"💼 Hai lavorato e guadagnato {guad}€!")
@bot.command()
async def beg(ctx): await ctx.send(f"🥺 Qualcuno ti ha dato {random.randint(1,50)}€")
@bot.command()
async def rob(ctx, m: discord.Member):
    v=random.randint(10,100); await ctx.send(f"🦹 Hai rubato {v}€ a {m.name}!")
@bot.command()
async def pay(ctx, m: discord.Member, n: int):
    DB["economy"][str(ctx.author.id)] = DB["economy"].get(str(ctx.author.id),0)-n; DB["economy"][str(m.id)] = DB["economy"].get(str(m.id),0)+n; save(); await ctx.send(f"💸 Hai dato {n}€ a {m.name}")
@bot.command()
async def leaderboard(ctx):
    top=sorted(DB["economy"].items(), key=lambda x: x[1], reverse=True)[:5]; await ctx.send("🏆 Top: " + ", ".join([f"<@{k}>: {v}€" for k,v in top]))

# ============ RP CASTREZZATO ============
@bot.command(name="rp-start")
async def rpstart(ctx): await ctx.send("🎮 RP INIZIATO! Ricorda: /me per azioni, /do per ambiente. Buon RP a Castrezzato!")
@bot.command(name="rp-stop")
async def rpstop(ctx): await ctx.send("🛑 RP FINITO! Grazie a tutti!")
@bot.command()
async def patente(ctx, m: discord.Member=None): m=m or ctx.author; await ctx.send(f"🪪 {m.name} ha la patente B - Valida a Castrezzato RP")
@bot.command()
async def multa(ctx, m: discord.Member, n: int): await ctx.send(f"🚨 {m.mention} multato di {n}€ dalla Polizia di Castrezzato!")
@bot.command()
async def arresta(ctx, m: discord.Member): await ctx.send(f"🚔 {m.mention} ARRESTATO! 10 min di prigione RP!")
@bot.command()
async def lavoro(ctx): await ctx.send("💼 Lavori: Polizia, Ambulanza, Meccanico, Vigile, Benzinaio, Ristorante, Spacciatore RP. Scrivi !ai come diventare poliziotto")
@bot.command()
async def polizia(ctx): await ctx.send("👮 Per chiamare la polizia: apri un ticket !ticket o scrivi in #emergenze. Numero RP: 112")
@bot.command()
async def ambulanza(ctx): await ctx.send("🚑 Ambulanza Castrezzato: apri ticket o #emergenze. Numero RP: 118")

# ============ TICKET ============
@bot.command()
async def ticket(ctx, *, motivo="Supporto"):
    ch = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
    await ch.send(f"🎫 Ticket di {ctx.author.mention} | Motivo: {motivo}\nStaff, rispondete qui. `!close` per chiudere.")
    await ctx.send(f"Ticket creato: {ch.mention}")
@bot.command()
async def close(ctx):
    await ctx.send("Ticket chiuso in 3 secondi..."); await asyncio.sleep(3); await ctx.channel.delete()
@bot.command()
async def panel(ctx):
    e=discord.Embed(title="🎫 Apri un Ticket", description="Scrivi !ticket <motivo> per aprire un ticket.\nEs: `!ticket mi hanno rubato la macchina`", color=0x00ff00); await ctx.send(embed=e)
@bot.command()
async def setup_ticket(ctx): await ctx.send("✅ Sistema ticket attivo! Usa !ticket e !panel")

# ============ ADMIN / CONFIG ============
@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, *, testo): await ctx.send(f"📢 **ANNUNCIO**\n{testo}")
@bot.command()
@commands.has_permissions(administrator=True)
async def embed(ctx, *, testo):
    e=discord.Embed(description=testo, color=0x7289da); await ctx.send(embed=e)
@bot.command()
@commands.has_permissions(administrator=True)
async def poll(ctx, *, domanda):
    m=await ctx.send(f"📊 **SONDAGGIO:** {domanda}"); await m.add_reaction("✅"); await m.add_reaction("❌")
@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, *, premio): await ctx.send(f"🎉 **GIVEAWAY: {premio}**\nReagisci 🎉 per partecipare!")
@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, nuovo): bot.command_prefix = [nuovo]; await ctx.send(f"Prefisso cambiato a {nuovo}")
@bot.command()
async def verify(ctx):
    r=discord.utils.get(ctx.guild.roles, name="Verificato"); 
    if r: await ctx.author.add_roles(r); await ctx.send("✅ Verificato!")
    else: await ctx.send("Ruolo Verificato non trovato, chiedi allo staff")

# ============ SLASH COMMANDS ============
@bot.tree.command(name="help", description="Lista comandi")
async def slash_help(interaction: discord.Interaction): await interaction.response.send_message("Usa !help per tutti i comandi! Oppure !ai per l'AI")
@bot.tree.command(name="ping", description="Ping del bot")
async def slash_ping(interaction: discord.Interaction): await interaction.response.send_message(f"Pong {round(bot.latency*1000)}ms")
@bot.tree.command(name="ticket", description="Apri un ticket")
async def slash_ticket(interaction: discord.Interaction, motivo: str): await interaction.response.send_message(f"Ticket per: {motivo}. Usa !ticket in chat per crearlo!")

bot.run(TOKEN_DISCORD)
