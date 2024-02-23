import os
import discord
import message_handler
import notification_handler
import config
import asyncio
import logging
import sys
from dotenv import load_dotenv
import sheet_handler

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] - %(message)s', stream=sys.stdout)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot_started = False
notification_channel = None

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    global bot_started
    if not bot_started:
        for guild in client.guilds:
            config.guilds.append(guild)

        sheet_handler.load_sheet()

        notification_handler.queue_all_from_sheet()
        bot_started = True

@client.event
async def on_message(message):
    logging.info('New message from [{}] in channel [{}] :: {}'.format(str(message.author.name), str(message.channel.name), str(message.content)))

    if client.user == message.author:
        return
    # elif message.content.startswith('test'):
    elif message.content.lower().strip().startswith("!tod menu"):
        logging.info("reloading sheet...")
        await sheet_handler.reload_sheet()
        logging.info("sending menu...")
        await notification_channel.send(notification_handler.get_menu_messages())
    elif message.content.lower().startswith('!tod'):
        try:
            mob, time_of_death = message_handler.ingest_message(message)
            logging.info("message handled, updating sheet...")
            sheet_handler.update_sheet(mob, time_of_death)
            logging.info("sheet updated, adding thumbs up...")

            await message.add_reaction(config.thumbs_up)
            logging.info("message thumbs'd up")

        except Exception as e:
            logging.info('An error occured handling the message: {}'.format(str(e)))

        notification_handler.update_messages_for_mob(mob)
        logging.info("messages updated for mob [{}]".format(mob))


async def start_discord():
    await client.start(token)

async def start_notification_thread():
    await asyncio.sleep(10)
    logging.info('starting notifications')
    # await notification_handler.test_notifications()

    global notification_channel
    notification_channel = None

    for guild in config.guilds:
        logging.info(guild.name)
        if guild.name == config.guild_name:
            for channel in guild.text_channels:

                if channel.name == config.notification_channel:
                    logging.info('sending notifications in guild - {}'.format(guild.name))
                    logging.info('notification channel - {}'.format(channel.name))
                    notification_channel = channel


    while True:

        if notification_channel is not None:
            messages_to_send = notification_handler.get_notifications_to_send()
            # logging.info(messages_to_send)
            for message in messages_to_send:
                # message = '@here ' + message
                await notification_channel.send(message)

        # sheet_handler.reload_sheet()
        notification_handler.queue_all_from_sheet()
        await asyncio.sleep(60)

loop = asyncio.get_event_loop()

asyncio.ensure_future(start_notification_thread())
asyncio.ensure_future(start_discord())


loop.run_forever()

