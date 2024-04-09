import logging
import os
import sys
import discord
from discord.ext import commands
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

client = commands.Bot(command_prefix="/", intents=discord.Intents.all(), case_insensitive=True, self_bot=True)

report_channel = ""
channels = {}
motitor_mode = "blacklist"

# Define a command to change the report channel
@client.command(name="report")
async def report_in(ctx, channel):
    report_channel = channel
    await ctx.send(f"Now reporting harassment in {channel}.")


# Define a command to edit monitored channel list
@client.command(name="monitor")
async def remove_game_channel(ctx, operation, channel):
    # Check if the game exists
    match operation:
      case "add":
            channels.add(channel)
            await ctx.send(f"{channel} is added to the {motitor_mode}.")

      case "del":
            channels.remove(channel)
            await ctx.send(f"{channel} is removed to the {motitor_mode}.")
      case "clear":
            channels.clear()
            await ctx.send(f"The {motitor_mode} is cleared.")
      case "list":
            await ctx.send(f"{motitor_mode} :".join(channels)})
      case _:
            await ctx.send(f"{operation} is not a valid operation. Try add or del")

# Define a command to set the monitor list mode
@client.command(name="mode")
async def set_monitor_mode(ctx, mode):
    # Check if the game exists
    if mode not in ["blacklist", "whitelist"]:
        await ctx.send(f"Mode is either blacklist or whitelist")
    else:
        motitor_mode = mode
        await ctx.send(f"Monitoring is now in {mode} mode")
            
# Define a command to move a user to a channel when they launch a game
@client.event
async def on_message(member, before, after):
    # Check if the message is in a monitored channel
    match motitor_mode:
        case "whitelist":
            if after.channel not in channels:
                return
        case "blacklist":
            if after.channel in channels:
                return
    #Code here




def main() -> int:
    # Run the bot
    try:
        keys = load(sys.file('private/api-keys.yaml', 'r'))
    except exception:
        print("Error in configuration file:" + exception)
    if keys is None:
        log.fatal("private/api-keys.yaml file is invalid")
    if keys.discord_token is None:
        log.fatal("discord_token key not found in private/api-keys.yaml")
    client.run(keys.discord_token)
    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit