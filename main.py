import discord
from discord.ext import commands
from groq import Groq
import os

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
CHIAVE_GROQ = os.getenv("CHIAVE_GROQ")

client_groq = Groq(api_key=CHIAVE_GROQ)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user not in message.mentions and not message.content.startswith("!ai"):
        await bot.process_commands(message)
        return

    domanda = message.content.replace(f"<@{bot.user.id}>", "").replace("!ai", "").strip()
    if not domanda:
        await message.channel.send("Ciao! 👋 Sono l'AI di Castrezzato RP. Chiedimi qualsiasi cosa!")
        return

    async with message.channel.typing():
        try:
            risposta = client_groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Sei l'assistente AI di Castrezzato RP, server RP su Roblox. Rispondi in italiano, corto, simpatico e utile. Aiuta con regole, ticket, staff, problemi in game. Se è un problema serio, dì di aprire un ticket."},
                    {"role": "user", "content": domanda}
                ],
                max_tokens=500
            )
            await message.channel.send(risposta.choices[0].message.content[:2000])
        except:
            await message.channel.send("Scusa, ho avuto un problema. Riprova tra poco!")

    await bot.process_commands(message)

bot.run(TOKEN_DISCORD)
