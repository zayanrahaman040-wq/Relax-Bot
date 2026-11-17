import discord
from discord.ext import commands
from groq import Groq
import os
import random
import json
import asyncio
import datetime

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
CHIAVE_GROQ = os.getenv("CHIAVE_GROQ")
client_groq = Groq(api_key=CHIAVE_GROQ) if CHIAVE_GROQ else None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
bot.remove_command("help")

try:
    with open("data.json") as f:
        DB = json.load(f)
except:
    DB = {"warn": {}, "economy": {}}

def save():
    with open("data.json", "w") as f:
        json.dump(DB, f)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")
    await bot.change_presence(activity=discord.Game(name="/help | Castrezzato RP"))
    try:
        synced = await bot.tree.sync()
        print(f"Syncati {len(synced)} comandi slash!")
    except Exception as e:
        print(f"Errore sync: {e}")

@bot.event
async def on_member_join(m):
    ch = discord.utils.get(m.guild.text_channels, name="benvenuto")
    if ch:
        await ch.send(f"Benvenuto {m.mention} in {m.guild.name}! Fai /verify")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot.user in message.mentions:
        domanda = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if domanda:
            async with message.channel.typing():
                try:
                    r = client_groq.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": "Sei assistente Castrezzato RP. Italiano, corto."},
                            {"role": "user", "content": domanda}
                        ],
                        max_tokens=500
                    )
                    await message.channel.send(r.choices[0].message.content[:2000])
                except Exception as e:
                    await message.channel.send(f"Errore: {e}")
            return
    await bot.process_commands(message)

@bot.hybrid_command(name="help", description="Lista 100 comandi")
async def help_cmd(ctx, categoria: str = None):
    e = discord.Embed(title="Zayan Bot - 100 Comandi /", color=0x7289da)
    e.description = "Moderazione: /ban /kick /mute /unmute /timeout /warn /warnings /clear /purge /slowmode /lockdown /unlock /nick /giverole /removerole /nuke\nUtility: /ping /userinfo /serverinfo /avatar /botinfo /invite /uptime /id /say /orario /calcola\nFun: /coinflip /dice /rps /8ball /meme /joke /ship /rate /roast /compliment /hug /kiss /slap /flip /love /dado /slot /indovina /scelta /fortuna\nEconomia: /balance /daily /work /beg /rob /pay /leaderboard /shop /buy\nRP: /rp-start /rp-stop /patente /multa /arresta /lavoro /polizia /ambulanza /meccanico /rapina /fuga /citta\nTicket: /ticket /close /panel /setup_ticket\nAdmin: /announce /embed /poll /giveaway /setprefix /verify /sondaggio /regole\nExtra: /traducimi /meteo /sasso /carta /forbice /ciao /buongiorno /buonanotte /gg /lol /bravo /scusa /grazie /auguri /top /staff /segnala /idea\nAI: /ai"
    await ctx.send(embed=e)

@bot.hybrid_command(name="ai", description="Chiedi all AI")
async def ai_cmd(ctx, domanda: str):
    async with ctx.typing():
        try:
            r = client_groq.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "Sei assistente Castrezzato RP. Italiano, corto."},
                    {"role": "user", "content": domanda}
                ],
                max_tokens=500
            )
            await ctx.send(r.choices[0].message.content[:2000])
        except Exception as e:
            await ctx.send(f"Errore: {e}")

@bot.hybrid_command(name="ban", description="Banna un utente")
@commands.has_permissions(ban_members=True)
async def ban(ctx, m: discord.Member, motivo: str = "Nessun motivo"):
    await m.ban(reason=motivo)
    await ctx.send(f"Bannato {m}: {motivo}")

@bot.hybrid_command(name="kick", description="Kicka un utente")
@commands.has_permissions(kick_members=True)
async def kick(ctx, m: discord.Member, motivo: str = ""):
    await m.kick(reason=motivo)
    await ctx.send(f"Kickato {m}")

@bot.hybrid_command(name="mute", description="Muta un utente")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, m: discord.Member, min: int = 10):
    await m.timeout(datetime.timedelta(minutes=min))
    await ctx.send(f"Mutato {m} per {min} min")

@bot.hybrid_command(name="unmute", description="Smuta un utente")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, m: discord.Member):
    await m.timeout(None)
    await ctx.send(f"Smutato {m}")

@bot.hybrid_command(name="timeout", description="Timeout utente")
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, m: discord.Member, min: int = 10):
    await m.timeout(datetime.timedelta(minutes=min))
    await ctx.send(f"Timeout {min} min a {m}")

@bot.hybrid_command(name="warn", description="Warn utente")
async def warn(ctx, m: discord.Member, motivo: str = ""):
    DB["warn"].setdefault(str(m.id), []).append(motivo)
    save()
    await ctx.send(f"Warn a {m}: {motivo}")

@bot.hybrid_command(name="warnings", description="Vedi warn")
async def warnings(ctx, m: discord.Member):
    await ctx.send(f"Warn di {m}: {DB['warn'].get(str(m.id), [])}")

@bot.hybrid_command(name="clear", description="Cancella messaggi")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, n: int = 10):
    await ctx.channel.purge(limit=n+1)
    await ctx.send(f"Cancellati {n}", delete_after=3)

@bot.hybrid_command(name="purge", description="Cancella messaggi")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, n: int = 10):
    await ctx.channel.purge(limit=n+1)

@bot.hybrid_command(name="slowmode", description="Slowmode canale")
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, sec: int = 0):
    await ctx.channel.edit(slowmode_delay=sec)
    await ctx.send(f"Slowmode {sec}s")

@bot.hybrid_command(name="lockdown", description="Blocca canale")
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Canale bloccato")

@bot.hybrid_command(name="unlock", description="Sblocca canale")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Canale sbloccato")

@bot.hybrid_command(name="nick", description="Cambia nick")
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, m: discord.Member, nuovo: str = ""):
    await m.edit(nick=nuovo)
    await ctx.send(f"Nick cambiato a {nuovo}")

@bot.hybrid_command(name="giverole", description="Dai un ruolo")
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, m: discord.Member, r: discord.Role):
    await m.add_roles(r)
    await ctx.send(f"Dato {r} a {m}")

@bot.hybrid_command(name="removerole", description="Togli un ruolo")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, m: discord.Member, r: discord.Role):
    await m.remove_roles(r)
    await ctx.send(f"Tolto {r} a {m}")

@bot.hybrid_command(name="nuke", description="Ricrea canale")
@commands.has_permissions(manage_messages=True)
async def nuke(ctx):
    await ctx.channel.clone(reason="Nuke")
    await ctx.channel.delete()

@bot.hybrid_command(name="ping", description="Ping bot")
async def ping(ctx):
    await ctx.send(f"Ping {round(bot.latency*1000)}ms")

@bot.hybrid_command(name="userinfo", description="Info utente")
async def userinfo(ctx, m: discord.Member = None):
    m = m or ctx.author
    e = discord.Embed(title=m.name, color=m.color)
    e.add_field(name="ID", value=m.id)
    e.add_field(name="Entrato", value=m.joined_at.strftime("%d/%m/%Y"))
    if m.avatar:
        e.set_thumbnail(url=m.avatar.url)
    await ctx.send(embed=e)

@bot.hybrid_command(name="serverinfo", description="Info server")
async def serverinfo(ctx):
    g = ctx.guild
    await ctx.send(f"{g.name} | Membri: {g.member_count} | Canali: {len(g.channels)}")

@bot.hybrid_command(name="avatar", description="Vedi avatar")
async def avatar(ctx, m: discord.Member = None):
    m = m or ctx.author
    if m.avatar:
        await ctx.send(m.avatar.url)
    else:
        await ctx.send("Nessun avatar")

@bot.hybrid_command(name="botinfo", description="Info bot")
async def botinfo(ctx):
    await ctx.send(f"Zayan Bot | 100 comandi | Server: {len(bot.guilds)} | Ping: {round(bot.latency*1000)}ms")

@bot.hybrid_command(name="invite", description="Link invito")
async def invite(ctx):
    await ctx.send("Invita: https://discord.com/oauth2/authorize?client_id=TUO_ID&permissions=8&scope=bot%20applications.commands")

@bot.hybrid_command(name="uptime", description="Bot online?")
async def uptime(ctx):
    await ctx.send("Bot online")

@bot.hybrid_command(name="id", description="Vedi il tuo ID")
async def id_cmd(ctx):
    await ctx.send(f"Il tuo ID e: {ctx.author.id}")

@bot.hybrid_command(name="say", description="Il bot ripete")
async def say(ctx, testo: str):
    await ctx.send(testo)

@bot.hybrid_command(name="orario", description="Che ora e?")
async def orario(ctx):
    ora = datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
    await ctx.send(f"Ora: {ora}")

@bot.hybrid_command(name="calcola", description="Calcolatrice")
async def calcola(ctx, espressione: str):
    try:
        ris = eval(espressione)
        await ctx.send(f"{espressione} = {ris}")
    except:
        await ctx.send("Errore, prova /calcola 2+2")

@bot.hybrid_command(name="coinflip", description="Testa o croce")
async def coinflip(ctx):
    await ctx.send(random.choice(["Testa!", "Croce!"]))

@bot.hybrid_command(name="dice", description="Tira dado")
async def dice(ctx):
    await ctx.send(f"Dado: {random.randint(1,6)}")

@bot.hybrid_command(name="rps", description="Sasso carta forbice")
async def rps(ctx, scelta: str):
    b = random.choice(["carta", "forbice", "sasso"])
    await ctx.send(f"Tu: {scelta} | Io: {b}")

@bot.hybrid_command(name="8ball", description="Palla magica")
async def ball(ctx, domanda: str):
    await ctx.send(random.choice(["Si", "No", "Forse", "Sicuramente!", "Non credo"]))

@bot.hybrid_command(name="meme", description="Meme random")
async def meme(ctx):
    await ctx.send("Quando dici ultima partita e sono le 3 di notte")

@bot.hybrid_command(name="joke", description="Barzelletta")
async def joke(ctx):
    await ctx.send(random.choice(["Perche il pollo attraversa la strada? Per andare dall altra parte!", "Cosa fa un server stanco? Va in crash!"]))

@bot.hybrid_command(name="ship", description="Compatibilita")
async def ship(ctx, a: discord.Member, b: discord.Member = None):
    b = b or ctx.author
    perc = random.randint(0, 100)
    await ctx.send(f"{a.name} + {b.name} = {perc}%")

@bot.hybrid_command(name="rate", description="Vota qualcosa")
async def rate(ctx, cosa: str):
    await ctx.send(f"Do a {cosa} un {random.randint(1,10)}/10")

@bot.hybrid_command(name="roast", description="Prendi in giro")
async def roast(ctx, m: discord.Member = None):
    m = m or ctx.author
    await ctx.send(f"{m.mention} sei cosi lento che pure la WiFi ti supera")

@bot.hybrid_command(name="compliment", description="Complimento")
async def compliment(ctx, m: discord.Member = None):
    m = m or ctx.author
    await ctx.send(f"{m.mention} sei un grande!")

@bot.hybrid_command(name="hug", description="Abbraccia")
async def hug(ctx, m: discord.Member):
    await ctx.send(f"{ctx.author.mention} abbraccia {m.mention}")

@bot.hybrid_command(name="kiss", description="Bacia")
async def kiss(ctx, m: discord.Member):
    await ctx.send(f"{ctx.author.mention} bacia {m.mention}")

@bot.hybrid_command(name="slap", description="Schiaffeggia")
async def slap(ctx, m: discord.Member):
    await ctx.send(f"{ctx.author.mention} schiaffeggia {m.mention}")

@bot.hybrid_command(name="flip", description="Lancia moneta")
async def flip(ctx):
    await ctx.send(random.choice(["Testa", "Croce"]))

@bot.hybrid_command(name="love", description="Test amore")
async def love(ctx, m: discord.Member):
    await ctx.send(f"Compatibilita con {m.name}: {random.randint(0,100)}%")

@bot.hybrid_command(name="dado", description="Dado 1-100")
async def dado(ctx):
    await ctx.send(f"Dado: {random.randint(1,100)}")

@bot.hybrid_command(name="slot", description="Slot machine")
async def slot(ctx):
    simboli = random.choices(["Ciliegia", "Limone", "Stella", "Diamante"], k=3)
    await ctx.send(f"Slot: {' | '.join(simboli)}")

@bot.hybrid_command(name="indovina", description="Indovina numero 1-10")
async def indovina(ctx, numero: int):
    v = random.randint(1, 10)
    if numero == v:
        await ctx.send(f"Era {v}! HAI VINTO!")
    else:
        await ctx.send(f"Era {v}! Riprova!")

@bot.hybrid_command(name="scelta", description="Scegli tra 2 cose")
async def scelta(ctx, a: str, b: str):
    await ctx.send(f"Scelgo: {random.choice([a, b])}")

@bot.hybrid_command(name="fortuna", description="Frase fortuna")
async def fortuna(ctx):
    await ctx.send(random.choice(["Oggi e il tuo giorno fortunato!", "Attento ai ticket", "Grande RP ti aspetta!", "Stasera vinci tutto!"]))

@bot.hybrid_command(name="balance", description="Vedi soldi")
async def balance(ctx, m: discord.Member = None):
    m = m or ctx.author
    soldi = DB["economy"].get(str(m.id), 0)
    await ctx.send(f"{m.name}: {soldi} euro")

@bot.hybrid_command(name="daily", description="Daily +100 euro")
async def daily(ctx):
    uid = str(ctx.author.id)
    DB["economy"][uid] = DB["economy"].get(uid, 0) + 100
    save()
    await ctx.send("Piu 100 euro daily!")

@bot.hybrid_command(name="work", description="Lavora")
async def work(ctx):
    g = random.randint(50, 300)
    uid = str(ctx.author.id)
    DB["economy"][uid] = DB["economy"].get(uid, 0) + g
    save()
    await ctx.send(f"Hai guadagnato {g} euro!")

@bot.hybrid_command(name="beg", description="Elemosina")
async def beg(ctx):
    await ctx.send(f"Hai ricevuto {random.randint(1,50)} euro")

@bot.hybrid_command(name="rob", description="Ruba")
async def rob(ctx, m: discord.Member):
    await ctx.send(f"Hai rubato {random.randint(10,100)} euro a {m.name}!")

@bot.hybrid_command(name="pay", description="Dai soldi")
async def pay(ctx, m: discord.Member, n: int):
    uid = str(ctx.author.id)
    mid = str(m.id)
    DB["economy"][uid] = DB["economy"].get(uid, 0) - n
    DB["economy"][mid] = DB["economy"].get(mid, 0) + n
    save()
    await ctx.send(f"Hai dato {n} euro a {m.name}")

@bot.hybrid_command(name="leaderboard", description="Classifica soldi")
async def leaderboard(ctx):
    top = sorted(DB["economy"].items(), key=lambda x: x[1], reverse=True)[:5]
    testo = ", ".join([f"<@{k}>: {v} euro" for k, v in top])
    await ctx.send(f"Top: {testo}")

@bot.hybrid_command(name="shop", description="Negozio RP")
async def shop(ctx):
    await ctx.send("Shop: /buy auto 5000 euro | /buy casa 20000 euro | /buy telefono 500 euro")

@bot.hybrid_command(name="buy", description="Compra qualcosa")
async def buy(ctx, cosa: str):
    await ctx.send(f"Hai comprato {cosa}!")

@bot.hybrid_command(name="rp-start", description="Inizia RP")
async def rpstart(ctx):
    await ctx.send("RP INIZIATO! Buon RP a Castrezzato!")

@bot.hybrid_command(name="rp-stop", description="Finisci RP")
async def rpstop(ctx):
    await ctx.send("RP FINITO! Grazie a tutti!")

@bot.hybrid_command(name="patente", description="Patente RP")
async def patente(ctx, m: discord.Member = None):
    m = m or ctx.author
    await ctx.send(f"{m.name} ha patente B - Castrezzato RP")

@bot.hybrid_command(name="multa", description="Multa RP")
async def multa(ctx, m: discord.Member, n: int):
    await ctx.send(f"{m.mention} multato {n} euro dalla Polizia!")

@bot.hybrid_command(name="arresta", description="Arresta RP")
async def arresta(ctx, m: discord.Member):
    await ctx.send(f"{m.mention} ARRESTATO! 10 min prigione RP!")

@bot.hybrid_command(name="lavoro", description="Lavori RP")
async def lavoro(ctx):
    await ctx.send("Lavori: Polizia, Ambulanza, Meccanico, Vigile, Benzinaio, Ristorante. Fai /ai come diventare poliziotto")

@bot.hybrid_command(name="polizia", description="Chiama polizia")
async def polizia(ctx):
    await ctx.send("Polizia: /ticket o #emergenze. Numero RP: 112")

@bot.hybrid_command(name="ambulanza", description="Chiama ambulanza")
async def ambulanza(ctx):
    await ctx.send("Ambulanza: /ticket o #emergenze. Numero RP: 118")

@bot.hybrid_command(name="meccanico", description="Chiama meccanico")
async def meccanico(ctx):
    await ctx.send("Meccanico Castrezzato: /ticket per riparazione!")

@bot.hybrid_command(name="rapina", description="Rapina RP")
async def rapina(ctx):
    await ctx.send(f"{ctx.author.mention} sta facendo una rapina! Polizia in arrivo!")

@bot.hybrid_command(name="fuga", description="Fuga RP")
async def fuga(ctx):
    if random.random() > 0.5:
        await ctx.send(f"{ctx.author.mention} e riuscito a scappare!")
    else:
        await ctx.send(f"{ctx.author.mention} arrestato!")

@bot.hybrid_command(name="citta", description="Info citta")
async def citta(ctx):
    await ctx.send("Castrezzato RP - Citta Roblox RP. Regole in #regole, ticket con /ticket")

@bot.hybrid_command(name="ticket", description="Apri ticket")
async def ticket(ctx, motivo: str = "Supporto"):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    ch = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites=overwrites)
    await ch.send(f"Ticket di {ctx.author.mention} | {motivo} | /close per chiudere")
    await ctx.send(f"Ticket: {ch.mention}")

@bot.hybrid_command(name="close", description="Chiudi ticket")
async def close(ctx):
    await ctx.send("Chiuso in 3s...")
    await asyncio.sleep(3)
    await ctx.channel.delete()

@bot.hybrid_command(name="panel", description="Pannello ticket")
async def panel(ctx):
    e = discord.Embed(title="Apri un Ticket", description="Scrivi /ticket <motivo>\nEs: /ticket mi hanno rubato la macchina", color=0x00ff00)
    await ctx.send(embed=e)

@bot.hybrid_command(name="setup_ticket", description="Setup ticket")
async def setup_ticket(ctx):
    await ctx.send("Ticket attivo! Usa /ticket e /panel")

@bot.hybrid_command(name="announce", description="Annuncio")
@commands.has_permissions(administrator=True)
async def announce(ctx, testo: str):
    await ctx.send(f"ANNUNCIO\n{testo}")

@bot.hybrid_command(name="embed", description="Manda embed")
@commands.has_permissions(administrator=True)
async def embed(ctx, testo: str):
    e = discord.Embed(description=testo, color=0x7289da)
    await ctx.send(embed=e)

@bot.hybrid_command(name="poll", description="Sondaggio")
@commands.has_permissions(administrator=True)
async def poll(ctx, domanda: str):
    m = await ctx.send(f"SONDAGGIO: {domanda}")
    await m.add_reaction("✅")
    await m.add_reaction("❌")

@bot.hybrid_command(name="giveaway", description="Giveaway")
@commands.has_permissions(administrator=True)
async def giveaway(ctx, premio: str):
    await ctx.send(f"GIVEAWAY: {premio} Reagisci per partecipare!")

@bot.hybrid_command(name="setprefix", description="Cambia prefisso")
@commands.has_permissions(administrator=True)
async def setprefix(ctx, nuovo: str):
    bot.command_prefix = [nuovo]
    await ctx.send(f"Prefisso {nuovo}")

@bot.hybrid_command(name="verify", description="Verificati")
async def verify(ctx):
    r = discord.utils.get(ctx.guild.roles, name="Verificato")
    if r:
        await ctx.author.add_roles(r)
        await ctx.send("Verificato!")
    else:
        await ctx.send("Ruolo Verificato no trovato")
bot.run(TOKEN_DISCORD)
