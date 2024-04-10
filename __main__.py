import logging
import os
import sys
import discord
from discord.ext import commands
from yaml import load, dump
try:
    from yaml import SafeLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


logging.basicConfig(filename="logs.txt",
                    filemode='a', level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ADict(dict):
    def __init__(self, *args, **kwargs):
        super(ADict, self).__init__(*args, **kwargs)
        self.__dict__ = self

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all(), case_insensitive=True, self_bot=True)

report_channel = ""
channels = set()
monitor_mode = "blacklist"

config = None
lang = None

# Define a command to change the report channel
@bot.command(name="report")
async def report_in(ctx, channel):
    global report_channel, monitor_mode
    log.debug(f"report {channel}.")
    if monitor_mode == "blacklist":
      channels.remove(report_channel)
      channels.add(channel)
    else:
      channels.remove(channel)
    report_channel = channel
    #FIXME : Use lang everywhere with format
    await ctx.send(f"Now reporting harassment in {channel}.")


# Define a command to edit monitored channel list
@bot.command(name="monitor")
async def monitor(ctx, operation, channel):
    # Check if operation is correct and do it.
    log.debug(f"monitor {operation} {channel}.")
    match operation:
      case "add":
            channels.add(channel)
            await ctx.send(f"{channel} is added to the {monitor_mode}.")
      case "del":
            channels.remove(channel)
            await ctx.send(f"{channel} is removed to the {monitor_mode}.")
      case "clear":
            channels.clear()
            await ctx.send(f"The {monitor_mode} is cleared.")
      case "list":
            await ctx.send(f"{monitor_mode} :{channels}")
      case _:
            await ctx.send(f"{operation} is not a valid operation. Try add or del")

# Define a command to set the monitor list mode
@bot.command(name="mode")
async def set_monitor_mode(ctx, mode):
    # Check if mode exists
    global monitor_mode
    log.debug(f"monitor {operation} {channel}.")
    if mode not in ["blacklist", "whitelist"]:
        await ctx.send(f"Mode is either blacklist or whitelist")
    else:
        monitor_mode = mode
        await ctx.send(f"Monitoring is now in {mode} mode")
    monitor(ctx,"clear","")

# Says ehlo
@bot.event
async def on_ready():
    channel = bot.get_channel(1227522025720119296)
    await channel.send('EHLO')
    log.debug(f"EHLO")


# On each message check if monitored
@bot.event
async def on_message(message):
    # Check if the message is in a monitored channel
    match monitor_mode:
        case "whitelist":
            if message.channel not in channels:
                return
        case "blacklist":
            if message.channel in channels:
                return
    #TODO: Code here
    log.debug(f"Message monitored : {message}.")


def main() -> int: # Run the bot
    global config, lang, keys

    try:
        config = load(open('config.yml', 'r'), Loader=Loader)
    except Exception:
        log.fatal("Error in configuration file !")
    if config is None:
        log.fatal("config.yml is empty.")
    config = ADict(config)

    try:
        lang = load(open(f"lang/{config['lang']}.yml", 'r'), Loader=Loader)
    except Exception:
        log.fatal("Error in lang file !")
    if lang is None:
        log.fatal(f"lang/{config.lang}.yml is empty.")
    lang = ADict(lang)

    try:
        keys = load(open('private/api-keys.yml', 'r'), Loader=Loader)
    except Exception:
        log.fatal(lang.keys.error)
    if keys is None:
        log.fatal(lang.keys.empty)
    keys = ADict(keys)

    if keys.discord_token is None:
        log.fatal(lang.keys.no_discord)
    
    # Start the bot
    bot.run(keys.discord_token)
    return 0

if __name__ == '__main__':
    sys.exit(main())