import discord
from discord.ext import commands
import music
import os
from keep_alive import keep_alive

client = commands.Bot(command_prefix='!',intents = discord.Intents.all())
cogs = [music]
for i in range(len(cogs)):
  cogs[i].setup(client)


keep_alive()
client.run(os.environ['TOKEN'])
