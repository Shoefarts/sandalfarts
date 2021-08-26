import discord
from discord.ext import commands
import sys
sys.path.append("..")
from packages.fart import fart
import os
import datetime
import pandas as pd
import math
import asyncio

# Mongdb login credentials
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')

# Contains all commands related to XP competition
class guildWars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### Specific territory statistics ###
    @commands.command(
        help="Shows data available on a specific territory such as production information, current holder, etc.",
        brief="Shows data about a specific territory."
    )
    async def terrinfo(self, ctx, *, terrInput):

        confirmation = await ctx.channel.send('Request received, generating...')

        # Pulls API for list of terr owners
        URL = 'https://api.wynncraft.com/public_api.php?action=territoryList'
        fullTerrList = fart.requestget(URL)
        allTerrs = fullTerrList.get('territories')

        # Pulls information for all terrs
        terrData_df = fart.mongtodf(mongUser, mongPass, 'guildWars', 'terrData')
        terrData_df = terrData_df.drop(columns=['_id', 'index'])
        terrData_dict = terrData_df.set_index('territory').T.to_dict('dict')

        # If terr doesn't exist
        if terrInput.lower() not in [x.lower() for x in list(terrData_dict)]:
            embed = discord.Embed(title='__' + terrInput + '__', color=0x856c46)
            embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
            embed.add_field(name=terrInput + ' could not be found!',
                            value='> *Check your spelling?*',
                            inline=False)

        # Generate terr information embed
        else:
            # Cleanup input
            terrInd = [x.lower() for x in list(allTerrs)].index(terrInput.lower())
            terrName = allTerrs[list(allTerrs)[terrInd]]['territory']

            # Initializing information variables
            terrResource = terrData_dict[terrName]['resource']
            terrEmerald = terrData_dict[terrName]['emerald']
            terrBorders = terrData_dict[terrName]['borders']
            terrLocation = terrData_dict[terrName]['location']
            terrOwner = allTerrs[terrName]['guild']
            terrAcquired = allTerrs[terrName]['acquired']
            treasury = ['Very low', 'Low', 'Medium', 'High', 'Very high']
            timeandtreasury = fart.terrtimeandtreasury(allTerrs, terrName)
            treasurylvl = timeandtreasury[1]
            terrHold_str = timeandtreasury[0]

            # Calculates resource and emeralds
            [ore, crops, fish, wood, emerald] = fart.terrresandem(terrResource, terrEmerald)
            resandem_str = ''
            resandem_str += '> ' + str(emerald) + ' Emeralds'
            if ore != 0:
                resandem_str += '\n> ' + str(ore) + ' Ore'
            elif crops != 0:
                resandem_str += '\n> ' + str(crops) + ' Crops'
            elif fish != 0:
                resandem_str += '\n> ' + str(fish) + ' Fish'
            elif wood != 0:
                resandem_str += '\n> ' + str(wood) + ' Wood'

            # Creates border string
            borders_str = ''
            for terr in terrBorders[1]:
                borders_str += '> ' + terr + '\n'

            # Generating embed
            embed = discord.Embed(title='__' + terrName + '__ (' + str(terrLocation['x']) + ', ' + str(terrLocation['y']) + ')', color=0x856c46)
            embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
            embed.add_field(name='Resources:',
                            value=resandem_str,
                            inline=False)
            embed.add_field(name='Treasury Level:',
                            value='> ' + treasury[treasurylvl],
                            inline=False)
            embed.add_field(name='Current territory holder:',
                            value='> **' + terrOwner + '**\n> As of *' + terrAcquired + '*\n> Held for: *' + terrHold_str + '*',
                            inline=False)
            embed.add_field(name='Borders:',
                            value=borders_str,
                            inline=False)

        # Final wrapups
        print(ctx.author.display_name + 'requested information on ' + terrInput)
        await ctx.channel.send(embed=embed)
        await confirmation.delete()

    ### Guild territory statistics ###
    @commands.command(
        help="Brings up a list of territories currently head by a specific guild including their treasury levels too",
        brief="Creates a list of territories held by a guild"
    )
    async def guildterr(self, ctx, *, guildFullName):

        confirmation = await ctx.channel.send('Request received, generating...')

        # Get terr information
        terrData = fart.terrlistget(guildFullName)
        guildName = terrData[0]
        terrList = terrData[1]
        terrList = dict(sorted(terrList.items(), key=lambda k_v: k_v[1]['acquired']))
        terrCount = terrData[2]

        # Cleanup guild name
        guildFullName = guildFullName.title()

        # Initializing variables
        page = 0
        terrList_keys = list(terrList)
        embedPage = [0]
        treasury = ['Very low', 'Low', 'Medium', 'High', 'Very high']

        # Generating embed for no terrs
        if not terrList:
            embedPage[page] = discord.Embed(title=guildFullName + " Territory List [" + str(terrCount) + "]", color=0x856c46)
            embedPage[page].set_footer(text="Requested by: {}".format(ctx.author.display_name))
            embedPage[page].add_field(name=guildFullName + ' has no territories!',
                            value='> *Nothing to see here*',
                            inline=False)

        # Generating terr embed pages
        else:
            reqPage = math.ceil(len(terrList) / 10)
            ind = 0

            while page < reqPage:

                embedPage[page] = discord.Embed(title=guildName + " Territory List [" + str(terrCount) + "]", color=0x856c46)
                embedPage[page].set_footer(text='Requested by: ' + discord.utils.escape_markdown(ctx.author.display_name) + '')

                entry = 0
                while entry < 10:
                    if ind >= len(terrList):
                        break

                    else:
                        timeandtreasury = fart.terrtimeandtreasury(terrList, terrList_keys[ind])
                        terrHold_Str = timeandtreasury[0]
                        treasurylvl = timeandtreasury[1]

                        # Generating embed fields
                        embedPage[page].add_field(name=terrList_keys[ind],
                                    value='> Held for ' + terrHold_Str + '\n> Treasury level: **' + treasury[treasurylvl] + '**\n> Acquired at: *' + terrList[terrList_keys[ind]]['acquired'] + '*',
                                    inline=False)
                    entry += 1
                    ind += 1

                page += 1
                embedPage.extend(str(page))

        print(ctx.author.display_name + ' requested ' + guildName + ' territory list!')
        await confirmation.delete()

        # Sending embed and doing pages
        message = await ctx.send(embed=embedPage[0])
        await message.add_reaction('⏮')
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        await message.add_reaction('⏭')

        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None

        while True:
            if str(reaction) == '⏮':
                i = 0
                await message.edit(embed=embedPage[i])
            elif str(reaction) == '◀':
                if i > 0:
                    i -= 1
                    await message.edit(embed=embedPage[i])
            elif str(reaction) == '▶':
                if i < (page-1):
                    i += 1
                    await message.edit(embed=embedPage[i])
            elif str(reaction) == '⏭':
                i = (page-1)
                await message.edit(embed=embedPage[i])

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
            except:
                break

        await message.clear_reactions()


# Setup call
def setup(bot):
    bot.add_cog(guildWars(bot))