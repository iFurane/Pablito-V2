import discord
from discord.ext import commands
import datetime
import yaml
import os
import shlex
import toolbox

# Load tokens
with open(file='tokens.yml', mode='r') as f:
    tokens = yaml.safe_load(f)

# Global variables and containers
commands_data = {}  # Container for command data: format
state_data = {}     # Container for state data
colors_data = {}    # Container for color data
channel_data = {}   # Container for Channel data
reply_data = {}       # Container for reply formats
roles_data = {}       # Container for roles data
emojis_data = {}      # Container for emoji data
boot_time = 0       # UTC time at bot's connection

# Give all permissions to bot
intents = discord.Intents.all()
# Prefix is -
bot = commands.Bot(command_prefix='-', intents=intents)


# Event: bot connected
@bot.event
async def on_connect():
    print(f'{datetime.datetime.utcnow()}: {bot.user.name} has connected.')
    update()


# Event: bot ready
@bot.event
async def on_ready():
    global boot_time
    boot_time = datetime.datetime.utcnow()  # UTC time when bot connected
    print(f'{boot_time}: {bot.user.name} is ready.')    # Verify connection
    await log(text=f'{bot.user.name} is ready')


# Event: user joins
@bot.event
async def on_member_join(member):
    # ask user to verify via captcha in DM
    await log(text=f'{member}:{member.id} has joined the server. Bot verification pending')
    channel = bot.get_channel((channel_data['WELCOME']['ID']))
    embed = discord.Embed(title=f'Welcome to iServer, {member}',
                          description=f'{member.mention}, check message in your DM for verification process\n'
                                      f'We have {channel.guild.member_count} members now',
                          color=colors_data['DEFAULT'])
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'{datetime.datetime.utcnow()}')
    await channel.send(embed=embed)


# Verification:
# Generate a random alphanumerical string and ask the user to type it
# Give 3 tries within 120 seconds
# if answer matches then give all initial roles ( Verified, member, tag recall)
# if all tries fail then leave for manual verification
# async def verify_user(member):


# Event: member leaves
@bot.event
async def on_member_remove(member):
    await log(text=f'{member}:{member.id} has left the server')
    channel = bot.get_channel(channel_data['GOODBYE']['ID'])
    embed = discord.Embed(title=f'{member} has left the iServer',
                          description=f'We have {channel.guild.member_count} members now',
                          color=0x000000    # black,change later
                          )
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'{datetime.datetime.utcnow()}',icon_url=member.avatar_url)
    await channel.send(embed=embed)


# Role management commands:
# These commands can only be used in role menu channel
# Role, r: give role to the author
@bot.command(name='role')
async def r_role(ctx, *args):
    if ctx.channel.id != channel_data['ROLEMENU']['ID']:
        await react_prohib(ctx)
        await ctx.reply(f'This command can only be used in <#{channel_data["ROLEMENU"]["ID"]}>', delete_after=5)
        return
    query = ' '.join(args).lower()
    role = None
    for i in roles_data['member_roles']:
        if query == i:
            role = ctx.guild.get_role(int(roles_data[i]['id']))
            break
    if role is None:
        await react_neg(ctx)
        return
    await ctx.author.add_roles(role)
    await react_pos(ctx)
    return


# -removerole, -remr: Removes a member role
# Can only be used in rolemenu channel
@bot.command(name='removerole')
async def rem_role(ctx, *args):
    if ctx.channel.id != channel_data['ROLEMENU']['ID']:
        await react_neg(ctx)
        await ctx.reply(f'This command can only be used in <#{channel_data["ROLEMENU"]["ID"]}>', delete_after=5)
        return
    query = ' '.join(args).lower()
    role = None
    for i in roles_data['member_roles']:
        if query == i:
            role = ctx.guild.get_role(int(roles_data[i]['id']))
            break
    if role is None:
        await react_neg(ctx)
        return
    await ctx.author.remove_roles(role)
    await react_pos(ctx)
    return


# -setstatus: Set the bot's status
# args[0]: status type (playing, listening, watching , streaming)
# if type = stream, then args[0]: url of stream and args[1:]: status text
@bot.command(name='setstatus')
async def set_status(ctx, status_type='', *args):
    await react_loading(ctx)
    status = ' '.join(args)
    if status_type == 'watching':
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
    elif status_type == 'listening':
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
    elif status_type == 'playing':
        await bot.change_presence(activity=discord.Game(status))
    elif status_type == 'streaming':
        await bot.change_presence(activity=discord.Streaming(name=' '.join(args[1:]), url=args[0]))
    else:
        await unreact_loading(ctx)
        await react_neg(ctx)
        embed = syntax_error_embed(ctx, 'setstatus')
        await ctx.reply(embed=embed, delete_after=reply_data['syntax_error']['timeout'])
        return
    await unreact_loading(ctx)
    await ctx.message.add_reaction('✅')
    await log(f'Bot status changed')


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
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC',icon_url=ctx.author.avatar_url)
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
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC', icon_url=ctx.author.avatar_url)
    await ctx.reply(embed=embed)


@bot.command(name='emojiinfo')
async def emoji_info(ctx, name):
    emojis = ctx.guild.emojis
    await ctx.reply(f'{emojis}')


# -channelinfo: Gives information about the given channel, or the current channel if not specified
# @bot.command(name='channelinfo')
# -roleinfo: Gives information about the given role

# @bot.command(name='roleinfo')
# -memberinfo: Gives information about the given user, or of the author if no id or mention is given
@bot.command(name='memberinfo')
async def member_info(ctx, *args):
    await react_loading(ctx)
    query = ' '.join(args)
    if len(args) == 0:  # Nothing given: give author's info
        member = ctx.author
    elif query.isdigit():
        member = ctx.guild.get_member(int(query))
    elif query.startswith('<@!') and query.endswith('>'):
        member = ctx.guild.get_member(int(query[3:-1]))
    else:
        await unreact_loading(ctx)
        await ctx.reply('User not found')
        return
    if member is None:
        await unreact_loading(ctx)
        await ctx.reply('User either does not exist or is not a member of this server')
        return
    display_name = member.display_name
    username = member
    member_id = member.id
    join_date = member.joined_at
    roles = ''
    for rl in member.roles:
        roles += f'{rl.mention} '
    status = member.status
    member_since = datetime.datetime.utcnow() - join_date
    embed = discord.Embed(title=f'{display_name}',
                          description=f'**Username: {username}**\n'
                                      f'**Member ID: {member_id}**\n'
                                      f'Joined at: {join_date}\n'
                                      f'Member since: {member_since}\n'
                                      f'\nRoles: {roles}\n'
                                      f'\n*Status: {status}*\n',
                          color=member.color)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC', icon_url=ctx.author.avatar_url)
    await unreact_loading(ctx)
    await ctx.reply(embed=embed)


@bot.command(name='profilepic')
async def profile_pic(ctx, *args):
    await react_loading(ctx)
    member = ''
    if len(args) == 0:  # Nothing given: give author's info
        member = ctx.author
    elif args[0].isdigit():
        member = ctx.guild.get_member(int(args[0]))
    elif args[0].startswith('<@!') and args[0].endswith('>'):
        member = ctx.guild.get_member(int(args[0][3:-1]))
    else:
        await unreact_loading(ctx)
        await ctx.reply('User not found')
        return
    if member is None:
        await unreact_loading(ctx)
        await ctx.reply('User either does not exist or is not a member of this server')
        return
    embed = discord.Embed(title=f'{member}\'s profile pic',
                          color=colors_data['DEFAULT'])
    embed.set_image(url=member.avatar_url)
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC', icon_url=ctx.author.avatar_url)
    await unreact_loading(ctx)
    await ctx.reply(embed=embed)


@bot.command(name='pablitohelp')
async def pablito_help(ctx):
    embed = discord.Embed(title=f'Pablito help',
                          description=f'Check {bot.get_channel(channel_data["DOCS"]["ID"]).mention} for help',
                          color=colors_data['DEFAULT'])
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC', icon_url=ctx.author.avatar_url)
    await ctx.reply(embed=embed,delete_after=15)


# -say: reply with the given string
@bot.command(name='say')
async def say(ctx, message):
    if ctx != '':
        await ctx.reply(f'{message}')
    else:
        return


# Create an embed for syntax errors
def syntax_error_embed(ctx, command):
    embed=discord.Embed(title=f'Syntax Error!',
                        description=f'Correct syntax is:\n'
                                    f'`{commands_data[command]["syntax"]}`\n'
                                    f'or\n'
                                    f'`{commands_data[command]["min_syntax"]}`',
                        color=reply_data['syntax_error']['color']
                        )
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC', icon_url=ctx.author.avatar_url)
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

    global roles_data
    with open('roles.yml','r') as fro:
        roles_data = yaml.safe_load(fro)

    #global emojis_data
    #with open('emojis.yml','r') as fe:
    #    emojis_data = yaml.safe_load(fe)


async def react_neg(ctx):
    await ctx.message.add_reaction('❌')
    return

async def react_pos(ctx):
    await ctx.message.add_reaction('✅')
    return

async def react_warn(ctx):
    await ctx.message.add_reaction('⚠️')
    return

async def react_prohib(ctx):
    await ctx.message.add_reaction('🚫')
    return

async def react_loading(ctx):
    await ctx.message.add_reaction(f'<a:loading:892783955386970182>')
    return

async def unreact_loading(ctx):
    await ctx.message.clear_reaction(f'<a:loading:892783955386970182>')

async def log(text):
    channel = bot.get_channel(channel_data['BOT_LOG']['ID'])
    await channel.send(f'{datetime.datetime.utcnow()} UTC: {text}')

bot.run(tokens['discord_token'])    # Run the bot
