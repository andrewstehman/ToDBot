import os
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
import message_handler

from dotenv import load_dotenv

import sheet_handler

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

global guild_name

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    global guild_name

    for guild in client.guilds:
        guild_name = guild.name
    #print("client :: %s" % client.user)
    print("guild :: %s" % guild_name)
    sheet_handler.load_sheet()

@client.event
async def on_message(message):
    print('New message :: ' + str(message.content))

    if client.user == message.author:
        return
    elif message.content.startswith('!ToD'):
        try:
            mob, time_of_death = message_handler.ingest_message(message)
            sheet_handler.update_sheet(mob, time_of_death)
            await message.add_reaction(u"\U0001F44D")
        except Exception as e:
            print('An error occured handling the message: {}'.format(str(e)))






#open_sheet()
# message_handler.test_function()
client.run(token)

