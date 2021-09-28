import discord
from discord.ext import commands
import asyncio
import yaml

TOKEN = ODM2MjU4OTgzMjY1Njk3ODU0.YIbY3g.VH0HJvlJJQ7ifbMt2AzXSMzjdkY

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name='Los Pollos Hermanos'))
    print(f'{bot.user.name} has connected.')

bot.run(TOKEN)
