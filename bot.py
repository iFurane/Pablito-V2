import discord
from discord.ext import commands
import datetime
import yaml

with open(file='tokens.yml',mode='r') as f:
    tokens = yaml.safe_load(f)

# Global variables and stores
commands_data = {}  # Container for command data
state_data = {}     # Container for state data, like status
colors_data = {}    # Container for color data
channel_data = {}    # Container for Channel IDs
reply_data={}
boot_time = 0       # UTC time at bot's connection

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)


#Event: bot ready
@bot.event
async def on_ready():
    global boot_time
    boot_time = datetime.datetime.utcnow()  # UTC time when bot connected
    update()    # Update all containers
    print(f'{bot.user.name} has connected. \n {boot_time}') # Verify connection


# Event: user joins
@bot.event
async def on_member_join(member):
    channel = bot.get_channel((channel_data['WELCOME']['ID']))
    embed = discord.Embed(title=f'Welcome to iServer, {member}',
                          description=f'{member.mention}, check message in your DM for verification process',
                          color=colors_data['DEFAULT'])
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'{datetime.datetime.utcnow()}')
    await channel.send(embed=embed)


# Event: member leaves
@bot.event
async def on_member_leave(member):
    channel = bot.get_channel(channel_data['GOODBYE'])


# -setstatus: Set the bot's status
# args[0]: status type (game, listen, watch , stream)
# if type = stream, then args[0]: url of stream
# other args: name
@bot.command(name='setstatus')
async def set_status(ctx, type='', *args):
    if type=='watch':
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=' '.join(args)))
    elif type=='listen':
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=' '.join(args)))
    elif type=='game':
        await bot.change_presence(activity=discord.Game(' '.join(args)))
    elif type=='stream':
        await bot.change_presence(activity=discord.Streaming(name=' '.join(args[1:]), url=args[0]))
    else:
        embed = syntax_error_embed(ctx, 'setstatus')
        await ctx.reply(embed=embed,delete_after=reply_data['syntax_error']['timeout'])
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


# -serverinfo: returns server's information
@bot.command(name='serverinfo')
async def server_info(ctx, *args):
    embed = discord.Embed(title=f'Server info',
                          description=f'Server name: {ctx.guild.name}\n'
                                      f'Created at: {ctx.guild.created_at}\n'
                                      f'Owner: {ctx.guild.owner}\n'
                                      f'Region: {ctx.guild.region}\n'
                                      f'Total Members: {ctx.guild.member_count}\n'
                                      f'Boost level: {ctx.guild.premium_tier}',
                          color=colors_data['DEFAULT']
                          )
    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC')
    await ctx.reply(embed=embed)


# -channelinfo: Gives information about the given channel, or the current channel if not specified
#@bot.command(name='channelinfo')
# -roleinfo: Gives information about the given role
#@bot.command(name='roleinfo')
# -userinfo: Gives information about the given user, or of the authir if not specified
#@bot.command(name='userinfo')


# Create an embed for syntax errors
def syntax_error_embed(ctx, command):
    embed=discord.Embed(title=f'Syntax Error!',
                        description=f'Correct syntax is:\n'
                                    f'`{commands_data[command]["syntax"]}`\n'
                                    f'or\n'
                                    f'`{commands_data[command]["min_syntax"]}`',
                        color=reply_data['syntax_error']['color']
                        )
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC')
    return embed


# Update all the value containers
def update():
    global commands_data
    with open('commands.yml', 'r') as fh:
        commands_data = yaml.safe_load(fh)

    global state_data
    with open('state.yml', 'r') as fs:
        state_data = yaml.safe_load(fs)

    global channel_data
    with open('channels.yml', 'r') as fc:
        channel_data = yaml.safe_load(fc)

    global colors_data
    with open('colors.yml', 'r') as fcl:
        colors_data = yaml.safe_load(fcl)

    global reply_data
    with open('reply.yml','r') as fr:
        reply_data = yaml.safe_load(fr)


bot.run(tokens['discord_token'])    # Run the bot
