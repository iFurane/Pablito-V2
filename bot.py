import discord
from discord.ext import commands
import datetime
import yaml

with open(file='tokens.yml',mode='r') as f:
    tokens = yaml.safe_load(f)

# Global variables and stores
help_data = {}      # Container for command help data
state_data = {}     # Container for state data, like status
colors_data = {}    # Container for color data
channel_ids = {}    # Container for Channel IDs
boot_time = 0       # UTC time at bot's connection

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.event
async def on_ready():
    global boot_time
    boot_time = datetime.datetime.utcnow()
    update()
    print(f'{bot.user.name} has connected. \n {boot_time}')


# -setstatus: Set the bot's status
# args[0]: status type (game, listen, watch , stream)
# if type = stream, then args[0]: url of stream
# other args: name
@bot.command(name='setstatus')
async def set_status(ctx, type, *args):
    if type=='watch':
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=' '.join(args)))
    elif type=='listen':
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=' '.join(args)))
    elif type=='game':
        await bot.change_presence(activity=discord.Game(' '.join(args)))
    elif type=='stream':
        await bot.change_presence(activity=discord.Streaming(name=' '.join(args[1:]), url=args[0]))
    else:
        await ctx.reply(f' Syntax error')
    print(f'status changed')


# -botinfo: Show information about the bot
# Name: bot's name
# Uptime: Bot's uptime
@bot.command(name='botinfo')
async def bot_info(ctx, *args):
    issue_time = datetime.datetime.utcnow()
    uptime = (issue_time - boot_time)
    embed = discord.Embed(title='Bot Info',
                          description=f'Bot name: {bot.user.name}\n'
                                      f'Uptime: {uptime}\n',
                          color=colors_data['DEFAULT'])
    embed.set_footer(text=f'{issue_time} UTC')
    await ctx.reply(embed=embed)


def update():   # Update all the value containers
    global help_data
    with open('help.yml', 'r') as fh:
        help_data = yaml.safe_load(fh)

    global state_data
    with open('state.yml', 'r') as fs:
        help_data = yaml.safe_load(fs)

    global channel_ids
    with open('channelids.yml', 'r') as fc:
        help_data = yaml.safe_load(fc)

    global colors_data
    with open('colors.yml', 'r') as fcl:
        colors_data = yaml.safe_load(fcl)


bot.run(tokens['discord_token'])    # Run the bot
