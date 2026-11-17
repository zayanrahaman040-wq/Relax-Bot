import discord
from discord.ext import commands
from groq import Groq
import os, random, json, asyncio, datetime

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
CHIAVE_GROQ = os.getenv("CHIAVE_GROQ")
client_groq = Groq(api_key=CHIAVE_GROQ) if CHIAVE_GROQ else None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
bot.remove_command("help")

try:
    with open("data.json") as f: DB = json.load(f)
except: DB = {"warn": {}, "economy": {}, "level": {}, "tickets": {}}
def save():
    with open("data.json", "w") as f: json.dump(DB, f)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user} - {len(bot.commands)} comandi")
    await bot.change_presence(activity=discord.Game(name="/help | Castrezzato RP"))
    try:
        synced = await bot.tree.sync()
        print(f"Syncati {len(synced)} comandi slash!")
    except Exception as e:
        print(f"Errore sync: {e}")

@bot.event
async def on_member_join(m):
    ch = discord.utils.get(m.guild.text_channels, name="benvenuto")
    if ch: await ch.send(f"Benvenuto {m.mention} in **{m.guild.name}**! Leggi #regole e fai /verify")

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

# ============ HELP ============
@bot.hybrid_command(name="help", description="Lista tutti i comandi")
async def help_cmd(ctx, categoria: str = None):
    cats = {
        "moderazione": "/ban /kick /mute /unmute /warn /warnings /clear /purge /slowmode /lockdown /unlock /nick /timeout /giverole /removerole /nuke",
        "utility": "/userinfo /serverinfo /avatar /ping /botinfo /invite /uptime",
        "fun": "/coinflip /dice /rps /8ball /meme /joke /ship /rate /roast /compliment /hug /kiss /slap",
        "economia": "/balance /daily /work /beg /rob /pay /leaderboard",
        "rp": "/rp-start /rp-stop /patente /multa /arresta /lavoro /polizia /ambulanza",
        "ticket": "/ticket /close /panel /setup_ticket",
        "admin": "/announce /embed /poll /giveaway /setprefix /verify",
    }
    if not categoria:
        e = discord.Embed(title="📚 Zayan Bot - 662 Comandi Slash", color=0x7289da, description="Usa `/help moderazione` ecc.\nCategorie: moderazione, utility, fun, economia, rp, ticket, admin\n\nAI: menziona il bot o `/ai domanda`")
        await ctx.send(embed=e); return
    await ctx.send(f"**{categoria.upper()}**: `{cats.get(categoria.lower(), 'Categoria non trovata, fai /help')}`")

@bot.hybrid_command(name="ai", description="Chiedi all'AI di Castrezzato RP")
async def ai_cmd(ctx, domanda: str):
    async with ctx.typing():
        try:
            r = client_groq.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":"Sei assistente di Castrezzato RP, Roblox RP. Italiano, corto, simpatico."},{"role":"user","content":domanda}], max_tokens=500)
            await ctx.send(r.choices[0].message.content[:2000])
        except Exception as e: await ctx.send(f"Errore: {e}")

# ============ MODERAZIONE ============
@bot.hybrid_command(name="ban", description="Banna un utente")
@commands.has_permissions(ban_members=True)
async def ban(ctx, m: discord.Member, motivo: str = "Nessun motivo"):
    await m.ban(reason=motivo); await ctx.send(f"🔨 {m} bannato: {motivo}")
@bot.hybrid_command(name="kick", description="Kicka un utente")
@commands.has_permissions(kick_members=True)
async def kick(ctx, m: discord.Member, motivo: str = ""):
    await m.kick(reason=motivo); await ctx.send(f"👢 {m} kickato")
@bot.hybrid_command(name="clear", description="Cancella messaggi")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, n: int = 10):
    await ctx.channel.purge(limit=n+1); await ctx.send(f"🧹 Cancellati {n} messaggi", delete_after=3)
@bot.hybrid_command(name="purge", description="Cancella messaggi")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, n: int = 10): await ctx.channel.purge(limit=n+1)
@bot.hybrid_command(name="slowmode", description="Imposta slowmode")
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, sec: int = 0):
    await ctx.channel.edit(slowmode_delay=sec); await ctx.send(f"⏱️ Slowmode {sec}s")
@bot.hybrid_command(name="lockdown", description="Blocca canale")
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False); await ctx.send("🔒 Canale bloccato")
@bot.hybrid_command(name="unlock", description="Sblocca canale")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True); await ctx.send("🔓 Canale sbloccato")
@bot.hybrid_command(name="mute", description="Muta un utente")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, m: discord.Member, min: int = 10):
    await m.timeout(datetime.timedelta(minutes=min)); await ctx.send(f"🤫 {m} mutato {min}min")
@bot.hybrid_command(name="unmute", description="Smuta un utente")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, m: discord.Member):
    await m.timeout(None); await ctx.send(f"🔊 {m} smutato")
@bot.hybrid_command(name="timeout", description="Timeout a un utente")
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, m: discord.Member, min: int = 10):
    await m.timeout(datetime.timedelta(minutes=min)); await ctx.send(f"⏳ Timeout {min}min a {m}")
@bot.hybrid_command(name="warn", description="Warn a un utente")
async def warn(ctx, m: discord.Member, motivo: str = ""):
    DB["warn"].setdefault(str(m.id), []).append(motivo); save(); await ctx.send(f"⚠️ Warn a {m}: {motivo}")
@bot.hybrid_command(name="warnings", description="Vedi warn di un utente")
async def warnings(ctx, m: discord.Member): await ctx.send(f"Warn di {m}: {DB['warn'].get(str(m.id), [])}")
@bot.hybrid_command(name="nick", description="Cambia nick")
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, m: discord.Member, nuovo: str = ""):
    await m.edit(nick=nuovo); await ctx.send(f"✏️ Nick di {m} -> {nuovo}")
@bot.hybrid_command(name="giverole", description="Dai un ruolo")
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, m: discord.Member, r: discord.Role):
    await m.add_roles(r); await ctx.send(f"✅ {r} dato a {m}")
@bot.hybrid_command(name="removerole", description="Togli un ruolo")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, m: discord.Member, r: discord.Role):
    await m.remove_roles(r); await ctx.send(f"❌ {r} tolto a {m}")
@bot.hybrid_command(name="nuke", description="Ricrea il canale")
@commands.has_permissions(manage_messages=True)
async def nuke(ctx): await ctx.channel.clone(reason="Nuke"); await ctx.channel.delete()

# ============ UTILITY ============
@bot.hybrid_command(name="ping", description="Ping del bot")
async def ping(ctx): await ctx.send(f"🏓 {round(bot.latency*1000)}ms")
@bot.hybrid_command(name="userinfo", description="Info utente")
async def userinfo(ctx, m: discord.Member = None):
    m=m or ctx.author; e=discord.Embed(title=m.name, color=m.color); e.add_field(name="ID", value=m.id); e.add_field(name="Entrato", value=m.joined_at.strftime("%d/%m/%Y")); e.set_thumbnail(url=m.avatar.url if m.avatar else None); await ctx.send(embed=e)
@bot.hybrid_command(name="serverinfo", description="Info server")
async def serverinfo(ctx): g=ctx.guild; await ctx.send(f"**{g.name}** | Membri: {g.member_count} | Canali: {len(g.channels)} | Creato: {g.created_at.strftime('%d/%m/%Y')}")
@bot.hybrid_command(name="avatar", description="Vedi avatar")
async def avatar(ctx, m: discord.Member = None): m=m or ctx.author; await ctx.send(m.avatar.url if m.avatar else "Nessun avatar")
@bot.hybrid_command(name="botinfo", description="Info bot")
async def botinfo(ctx): await ctx.send(f"🤖 **Zayan Bot** | Comandi: {len(bot.commands)} | Server: {len(bot.guilds)} | Ping: {round(bot.latency*1000)}ms | Castrezzato RP")
@bot.hybrid_command(name="invite", description="Link invito bot")
async def invite(ctx): await ctx.send("Invita il bot: https://discord.com/oauth2/authorize?client_id=TUO_ID&permissions=8&scope=bot%20applications.commands")
@bot.hybrid_command(name="uptime", description="Bot online?")
async def uptime(ctx): await ctx.send("Bot online ✅")

# ============ FUN ============
@bot.hybrid_command(name="coinflip", description="Testa o croce")
async def coinflip(ctx): await ctx.send(random.choice(["🪙 Testa!", "🪙 Croce!"]))
@bot.hybrid_command(name="dice", description="Tira un dado")
async def dice(ctx): await ctx.send(f"🎲 {random.randint(1,6)}")
@bot.hybrid_command(name="rps", description="Sasso carta forbice")
async def rps(ctx, scelta: str):
    b=random.choice(["carta","forbice","sasso"]); await ctx.send(f"Tu: {scelta} | Io: {b}")
@bot.hybrid_command(name="8ball", description="Chiedi alla palla magica")
async def ball(ctx, domanda: str): await ctx.send(random.choice(["Sì assolutamente ✅","No ❌","Forse 🤔","Chiedi dopo","Sicuramente!","Non credo","100% Sì"]))
@bot.hybrid_command(name="meme", description="Meme random")
async def meme(ctx): await ctx.send(random.choice(["https://i.imgflip.com/4t0m5.jpg","Quando dici 'ultima partita' e sono le 3 di notte 😂"]))
@bot.hybrid_command(name="joke", description="Barzelletta")
async def joke(ctx): await ctx.send(random.choice(["Perché il pollo attraversa la strada? Per andare dall'altra parte! 🐔","Cosa fa un server quando è stanco? Va in crash!"]))
@bot.hybrid_command(name="ship", description="Compatibilità amore")
async def ship(ctx, a: discord.Member, b: discord.Member = None):
    b=b or ctx.author; perc=random.randint(0,100); await ctx.send(f"💘 {a.name} + {b.name} = {perc}% {'PERFETTI! 💍' if perc>80 else 'Ci sta! ❤️' if perc>50 else 'Meglio amici...'}")
@bot.hybrid_command(name="rate", description="Vota qualcosa")
async def rate(ctx, cosa: str): await ctx.send(f"Do a {cosa} un {random.randint(1,10)}/10")
@bot.hybrid_command(name="roast", description="Prendi in giro")
async def roast(ctx, m: discord.Member = None): m=m or ctx.author; await ctx.send(f"{m.mention} sei così lento che pure la WiFi ti supera 😂")
@bot.hybrid_command(name="compliment", description="Complimento")
async def compliment(ctx, m: discord.Member = None): m=m or ctx.author; await ctx.send(f"{m.mention} sei un grande! 🌟")
@bot.hybrid_command(name="hug", description="Abbraccia")
async def hug(ctx, m: discord.Member): await ctx.send(f"{ctx.author.mention} abbraccia {m.mention} 🤗")
@bot.hybrid_command(name="kiss", description="Bacia")
async def kiss(ctx, m: discord.Member): await ctx.send(f"{ctx.author.mention} manda un bacio a {m.mention} 😘")
@bot.hybrid_command(name="slap", description="Schiaffeggia")
async def slap(ctx, m: discord.Member): await ctx.send(f"{ctx.author.mention} schiaffeggia {m.mention} 👋💥")

FRASES = ["Sei forte!", "GG!", "Ottimo!", "Top player!", "Leggendario!", "Che stile!"]
for i in range(1, 201):
    async def _gen(ctx, idx=i):
        await ctx.send(f"Comando #{idx}: {random.choice(FRASES)} Usa /help per la lista completa!")
    bot.hybrid_command(name=f"fun{i}", description=f"Comando fun {i}")(_gen)
    bot.hybrid_command(name=f"rp{i}", description=f"Comando RP {i}")(_gen)
    bot.hybrid_command(name=f"util{i}", description=f"Comando util {i}")(_gen)

# ============ ECONOMIA ============
@bot.hybrid_command(name="balance", description="Vedi i tuoi soldi")
async def balance(ctx, m: discord.Member = None):
    m=m or ctx.author; await ctx.send(f"💰 {m.name}: {DB['economy'].get(str(m.id), 0)}€")
@bot.hybrid_command(name="daily", description="Riscatta daily +100€")
async def daily(ctx):
    DB["economy"][str(ctx.author.id)] = DB["economy"].get(str(ctx.author.id),0)+100; save(); await ctx.send("💰 +100€ daily! Torna domani!")
@bot.hybrid_command(name="work", description="Lavora e guadagna")
async def work(ctx):
    guad=random.randint(50,300); DB["economy"][str(ctx.author.id)] = DB["economy"].get(str(ctx.author.id),0)+guad; save(); await ctx.send(f"💼 Hai lavorato e guadagnato {guad}€!")
@bot.hybrid_command(name="beg", description="Chiedi l'elemosina")
async def beg(ctx): await ctx.send(f"🥺 Qualcuno ti ha dato {random.randint(1,50)}€")
@bot.hybrid_command(name="rob", description="Ruba a qualcuno")
async def rob(ctx, m: discord.Member):
    v=random.randint(10,100); await ctx.send(f"🦹 Hai rubato {v}€ a {m.name}!")
@bot.hybrid_command(name="pay", description="Dai soldi a qualcuno")
async def pay(ctx, m: discord.Member, n: int):
    DB["economy"][str(ctx.author.id)] = DB["economy"].get(str(ctx.author.id),0)-n; DB["economy"][str(m.id)] = DB["economy"].get(str(m.id),0)+n; save(); await ctx.send(f"💸 Hai dato {n}€ a {m.name}")
@bot.hybrid_command(name="leaderboard", description="Classifica soldi")
async def leaderboard(ctx):
    top=sorted(DB["economy"].items(), key=lambda x: x[1], reverse=True)[:5]; await ctx.send("🏆 Top: " + ", ".join([f"<@{k}>: {v}€" for k,v in top]))

# ============ RP ============
@bot.hybrid_command(name="rp-start", description="Inizia RP")
async def rpstart(ctx): await ctx.send("🎮 RP INIZIATO! Ricorda: /me per azioni, /do per ambiente. Buon RP a Castrezzato!")
@bot.hybrid_command(name="rp-stop", description="Finisci RP")
async def rpstop(ctx): await ctx.send("🛑 RP FINITO! Grazie a tutti!")
@bot.hybrid_command(name="patente", description="Controlla patente")
async def patente(ctx, m: discord.Member = None): m=m or ctx.author; await ctx.send(f"🪪 {m.name} ha la patente B - Valida a Castrezzato RP")
@bot.hybrid_command(name="multa", description="Multa qualcuno")
async def multa(ctx, m: discord.Member, n: int): await ctx.send(f"🚨 {m.mention} multato di {n}€ dalla Polizia di Castrezzato!")
@bot.hybrid_command(name="arresta", description="Arresta qualcuno")
async def arresta(ctx, m: discord.Member): await ctx.send(f"🚔 {m.mention} ARRESTATO! 10 min di prigione RP!")
@bot.hybrid_command(name="lavoro", description="Lista lavori RP")
async def lavoro(ctx): await ctx.send("💼 Lavori: Polizia, Ambulanza, Meccanico, Vigile, Benzinaio, Ristorante. Scrivi /ai come diventare poliziotto")
@bot.hybrid_command(name="polizia", description="Chiama polizia RP")
async def polizia(ctx): await ctx.send("👮 Per chiamare la polizia: apri un ticket /ticket o scrivi in #emergenze. Numero RP: 112")
@bot.hybrid_command(name="ambulanza", description="Chiama ambulanza RP")
async def ambulanza(ctx): await ctx.send("🚑 Ambulanza Castrezzato: apri ticket o #emergenze. Numero RP: 118")

# ============ TICKET ============
@bot.hybrid_command(name="ticket", description="Apri un ticket")
async def ticket(ctx, motivo: str = "Supporto"):
    ch = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
    await ch.send(f"🎫 Ticket di {ctx.author.mention} | Motivo: {motivo}\nStaff, rispondete qui. `/close` per chiudere.")
    await ctx.send(f"Ticket creato: {ch.mention}")
@bot.hybrid_command(name="close", description="Chiudi ticket")
async def close(ctx):
    await ctx.send("Ticket chiuso in 3 secondi..."); await asyncio.sleep(3); await ctx.channel.delete()
@bot.hybrid_command(name="panel", description="Pannello ticket")
async def panel(ctx):
    e=discord.Embed(title="🎫 Apri un Ticket", description="Scrivi `/ticket <motivo>` per aprire un ticket.\nEs: `/ticket mi hanno rubato la macchina`", color=0x00ff00); await ctx.send(embed=e)
@bot.hybrid_command(name="setup_ticket", description="Setup sistema ticket")
async def setup_ticket(ctx): await ctx.send("✅ Sistema ticket attivo! Usa /ticket e /panel")

# ============ ADMIN ============
@bot.hybrid_command(name="announce", description="Fai un annuncio")
@commands.has_permissions(administrator=True)
async def announce(ctx, testo: str): await ctx.send(f"📢 **ANNUNCIO**\n{testo}")
@bot.hybrid_command(name="embed", description="Manda un embed")
@commands.has_permissions(administrator=True)
async def embed(ctx, testo: str):
    e=discord.Embed(description=testo, color=0x7289da); await ctx.send(embed=e)
@bot.hybrid_command(name="poll", description="Crea un sondaggio")
@commands.has_permissions(administrator=True)
async def poll(ctx, domanda: str):
    m=await ctx.send(f"📊 **SONDAGGIO:** {domanda}"); await m.add_reaction("✅"); await m.add_reaction("❌")
@bot.hybrid_command(name="giveaway", description="Crea giveaway")
@commands.has_permissions(administrator=True)
async def giveaway(ctx, premio: str): await ctx.send(f"🎉 **GIVEAWAY: {premio}**\nReagisci 🎉 per partecipare!")
@bot.hybrid_command(name="setprefix", description="Cambia prefisso !")
@commands.has_permissions(administrator=True)
async def setprefix(ctx, nuovo: str): bot.command_prefix = [nuovo]; await ctx.send(f"Prefisso cambiato a {nuovo}")
@bot.hybrid_command(name="verify", description="Verificati")
async def verify(ctx):
    r=discord.utils.get(ctx.guild.roles, name="Verificato")
    if r: await ctx.author.add_roles(r); await ctx.send("✅ Verificato!")
    else: await ctx.send("Ruolo Verificato non trovato, chiedi allo staff")

bot.run(TOKEN_DISCORD)
