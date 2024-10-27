import discord
from discord.ext import commands
import random

# Nastav token pre bota a názov kanála
TOKEN = ''
CHANNEL_NAME = '💬hlavný-chat🗨'  # Nahraď názov kanála podľa potreby

randomText = ["Ahoj", "", "@User1", "Daaaaaamnn", "xD", "čo ci pere", "LoL"]

# Inicializácia bota
intents = discord.Intents.default()
intents.messages = True  # Pre Python 3.7.3 použite 'intents.messages' namiesto 'intents.message_content'

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} je pripravený a pripojený!')

@bot.event
async def on_message(message):
    # Skontroluj, či správa nepochádza od bota, aby sa vyhol cyklickej reakcii
    if message.author == bot.user:
        return

    # Skontroluj, či správa bola napísaná v správnom kanáli
    if message.channel.name == CHANNEL_NAME:
        await message.channel.send(random.choice(randomText))  # Môžeš poslať náhodnú správu

    # Nezabudni na spracovanie ďalších príkazov
    await bot.process_commands(message)

# Spustenie bota
bot.run(TOKEN)
