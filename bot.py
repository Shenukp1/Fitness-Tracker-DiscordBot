import discord
from discord.ext import commands, tasks
import datetime
from datetime import date
from datetime import datetime
import json
import asyncio 
from text import TOKEN, G_CHANNEL_ID, R_CHANNEL_ID
from commands import setup_commands


#initalizies the bot
def initalize_bot():
    #discord required commands to make bot work
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    client = commands.Bot(command_prefix='!', intents=intents)#prefix used for commands



#to run the bot
def run_discord_bot():
    client = initalize_bot()
    setup_commands(client)#where all the commands are used
    client.run(TOKEN)