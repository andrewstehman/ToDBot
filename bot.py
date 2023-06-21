import asyncio
import os
import discord
import threading
import message_handler
import notification_handler
import config
import time
import asyncio

from dotenv import load_dotenv

import sheet_handler

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot_started = False

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    global bot_started
    if not bot_started:
        for guild in client.guilds:
            config.guilds.append(guild)

        sheet_handler.load_sheet()

        notification_handler.queue_all_from_sheet()
        bot_started = True

@client.event
async def on_message(message):
    print('New message :: {}'.format(str(message.author.name) + ' ' + str(message.content)))

    if client.user == message.author:
        return
    # elif message.content.startswith('test'):
    elif message.content.startswith('!ToD'):
        try:
            mob, time_of_death = message_handler.ingest_message(message)
            sheet_handler.update_sheet(mob, time_of_death)

            await message.add_reaction(config.thumbs_up)

        except Exception as e:
            print('An error occured handling the message: {}'.format(str(e)))

        notification_handler.update_messages_for_mob(mob)


async def start_discord():
    await client.start(token)

async def start_notification_thread():
    await asyncio.sleep(10)
    print('starting notifications')
    # await notification_handler.test_notifications()

    notification_channel = None

    for guild in config.guilds:
        print(guild.name)
        if guild.name == config.guild_name:
            for channel in guild.text_channels:

                if channel.name == config.notification_channel:
                    print('sending notifications in guild - {}'.format(guild.name))
                    print('notification channel - {}'.format(channel.name))
                    notification_channel = channel

    while True:

        if notification_channel is not None:
            messages_to_send = notification_handler.get_notifications_to_send()
            # print(messages_to_send)
            for message in messages_to_send:
                # message = '@here ' + message
                await channel.send(message)

        # sheet_handler.reload_sheet()
        notification_handler.queue_all_from_sheet()
        await asyncio.sleep(60)

loop = asyncio.get_event_loop()

asyncio.ensure_future(start_notification_thread())
asyncio.ensure_future(start_discord())


loop.run_forever()

