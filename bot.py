import asyncio
import discord
from discord.ext import commands
import datetime
import yaml
import os
import random
import hashlib
import shlex
import toolbox

# Load tokens
with open(file='data/tokens.yml', mode='r') as f:
    tokens = yaml.safe_load(f)

# Global variables and containers
commands_data = {}  # Container for command data: format
state_data = {}     # Container for state data
colors_data = {}    # Container for color data
channel_data = {}   # Container for Channel data
reply_data = {}       # Container for reply formats
roles_data = {}       # Container for roles data
guild_data = {}
emojis_data = {}      # Container for emoji data
boot_time = 0       # UTC time at bot's connection


# Prefix is -
# All permissions granted to the bot
bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())


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
    await log(text=f'{bot.user.name} is ready', event_type='Bot Connect')   # Bot connect event logged


# Event: user joins
@bot.event
async def on_member_join(member):
    # ask user to verify via captcha in DM
    await log(text=f'{member}:{member.id} has joined the server.', event_type='User Join')
    channel = bot.get_channel((channel_data['WELCOME']['ID']))
    embed = discord.Embed(title=f'Welcome to iServer, {member}',
                          description=f'{member.mention}, check message in your DM for verification process\n'
                                      f'We have {channel.guild.member_count} members now',
                          color=colors_data['POSITIVE'])
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'{datetime.datetime.utcnow()}')
    await channel.send(embed=embed)
    dm_channel = await member.create_dm()
    await dm_channel.send('Welcome to iServer!\n'
                          'To verify as a member, type `-verify` and follow the instructions.')


# Event: member leaves
@bot.event
async def on_member_remove(member):
    await log(text=f'{member}:{member.id} has left the server.',event_type='User Leave')
    channel = bot.get_channel(channel_data['GOODBYE']['ID'])
    embed = discord.Embed(title=f'{member} has left the iServer',
                          description=f'We have {channel.guild.member_count} members now',
                          color=colors_data['NEGATIVE']
                          )
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f'{datetime.datetime.utcnow()}',icon_url=member.avatar_url)
    await channel.send(embed=embed)


# Verification:
# Generate a random alphanumerical string and ask the user to type it
# Give 3 tries within 120 seconds
# if answer matches then give all initial roles ( Verified, member, tag recall)
# if all tries fail then leave for manual verification
# async def verify(ctx, **kwargs):
@bot.command(name='verify')
@commands.dm_only()
async def verify(ctx, **kwargs):
    verifee = ctx.message.author
    guild = bot.get_guild(guild_data['ID'])
    member = guild.get_member(verifee.id)
    common_role = guild.get_role(roles_data['member']['id'])
    await log(text=f'{member}:{member.id} initiated verification.', event_type='Verification')
    if common_role in member.roles:
        await ctx.send('You\'re already verified!')
        await log(f'{member}:{member.id} is already verified.', event_type='Verification')
        return
    passcode = hashlib.sha256((str(random.getrandbits(4096))+str(random.getrandbits(4096))).encode()).hexdigest()[0:state_data['verify_code_strength']]
    interaction = await ctx.send(f'Your verification code is: `{passcode}`\n'
                                  f'Message this code within 2 minutes to get verified.')
    def check(m):
        return isinstance(m.channel,discord.DMChannel)
    try:
        answer = await bot.wait_for('message',check=check, timeout=90)
    except asyncio.TimeoutError:
        await ctx.send('Timeout! Type `-verify` again to verify')
        await log(f'{member}:{member.id} failed code verification due to timeout', event_type='Verification')
        return
    # Check if code is correct
    if answer.content == passcode:
        final = await ctx.send(f"Code matched! Now click ✅ to complete verification.")
    else:
        await ctx.send('Code mismatch! Type `-verify` again to restart verification.')
        await log(f'{member}:{member.id} failed verification due to code mismatch.', event_type='Verification')
        return
    await final.add_reaction('✅')
    try:
        def check_2(reaction, user):
            return reaction.emoji == '✅' and user == ctx.author
        await bot.wait_for('reaction_add', check=check_2, timeout=90)
    except asyncio.TimeoutError:
        await ctx.send('Timeout! Type `-verify` again to verify')
        await log(f'{member}:{member.id} failed reaction verification due to timeout.', event_type='Verification')
        return
    try:
        await member.add_roles(common_role)
    except e:
        await ctx.send('An unknown error occured. Try `-verify` again. If the problem persists, contact the admin iFurane#3113.')
        return
    await log(f'{member}:{member.id} has been verified successfully!')


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
    embed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.reply(embed=embed)


# -serverinfo: returns server's information
@bot.command(name='serverinfo')
async def server_info(ctx, *args):
    embed = discord.Embed(title=f'Server info',
                          description=f'Server name: {ctx.guild.name}\n'
                                      f'Created at: {ctx.guild.created_at}\n'
                                      f'Owner: {ctx.guild.owner}\n'
                                      f'Total Members: {ctx.guild.member_count}\n'
                                      f'Boost level: {ctx.guild.premium_tier}',
                          color=colors_data['DEFAULT']
                          )
    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.set_footer(text=f'{ctx.author} at {datetime.datetime.utcnow()} UTC', icon_url=ctx.author.avatar_url)
    await ctx.reply(embed=embed)


@bot.command(name='memberinfo')
async def member_info(ctx, query=''):
    await react_loading(ctx)
    if query == '':  # Nothing given: give author's info
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


@bot.command(name='emojiinfo')
async def emoji_info(ctx, **kwargs):
    emojis = ctx.guild.emojis
    await ctx.reply(f'{emojis}')


# -channelinfo: Gives information about the given channel, or the current channel if not specified
# @bot.command(name='channelinfo')
# -roleinfo: Gives information about the given role

# @bot.command(name='roleinfo')
# -memberinfo: Gives information about the given user, or of the author if no id or mention is given

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
    if message != '':
        await ctx.reply(f'{message}')
    else:
        return


@bot.command(name='user')
async def user(ctx, member :discord.Member):
    if member is not None:
        await ctx.reply(str(member))



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
    with open('data/commands.yml', 'r') as fh:
        commands_data = yaml.safe_load(fh)

    global state_data
    with open('data/state.yml', 'r') as fs:
        state_data = yaml.safe_load(fs)

    global channel_data
    with open('data/channels.yml', 'r') as fc:
        channel_data = yaml.safe_load(fc)

    global colors_data
    with open('data/colors.yml', 'r') as fcl:
        colors_data = yaml.safe_load(fcl)

    global reply_data
    with open('data/reply.yml', 'r') as fr:
        reply_data = yaml.safe_load(fr)

    global roles_data
    with open('data/roles.yml', 'r') as fro:
        roles_data = yaml.safe_load(fro)

    global guild_data
    with open('data/guild.yml', 'r') as fg:
        guild_data = yaml.safe_load(fg)

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

async def log(text, event_type='Other'):
    channel = bot.get_channel(channel_data['BOT_LOG']['ID'])
    print(f'{datetime.datetime.utcnow()} UTC ({event_type}): {text}')
    await channel.send(f'*{datetime.datetime.utcnow()} UTC* **({event_type})**: {text}')

bot.run(tokens['discord_token'])    # Run the bot
