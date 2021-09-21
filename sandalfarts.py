from discord.ext import commands
import os

# Which bot to run?
discMode = "sandals"

# Bot Initialization
bot = commands.Bot(command_prefix=":sh ")
@bot.event
async def on_ready():
    print('Daddy {0.user} is here'.format(bot))

# Load commands
bot.load_extension("commands.xpCompSuite")
bot.load_extension("commands.clownTownExpress")
bot.load_extension("commands.guildWars")


# Bot token
if discMode == 'sandals':
    # For Sandals
    bot.run(os.getenv('TOKEN'))
elif discMode == 'proto':
    # For Proto
    bot.run(os.getenv('ProtoTOKEN'))
