import discord
from discord.ext import commands
from time import time
import sys
sys.path.append("..")
from packages.utils import gen
from packages.utils import xpcomp
import os
import pandas as pd
import math
import asyncio

# Mongdb login credentials
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')

# Class initialization
gen = gen()
xpcomp = xpcomp()

# Contains all commands related to XP competition
class xpCompSuite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### UUID Lookup ###
    @commands.command(
        help="Looks up UUID of given player IGN",
        brief="Looks up player UUID"
    )
    async def uuid(self, ctx, *, ign):

        # Confirmation of start
        confirmation = await ctx.channel.send('Request received, generating...')
        t0 = time()

        # Converts ign to uuid
        uuidPlayer = xpcomp.uuidfinder(ign)

        # Initializes embed item
        embedPage = discord.Embed(title=f"UUID Lookup", color=0x856c46)
        embedPage.set_footer(text='Requested by: ' + discord.utils.escape_markdown(ctx.author.display_name) + '')

        # If player ign doesn't exist
        if uuidPlayer[1] == "Error":
            embedPage.add_field(name='***ERROR***',
                                value='Specified player: ' + ign + ' does not exist!',
                                inline=False)
        else:
            embedPage.add_field(name='Data for input: ' + ign,
                                value='UUID: ' + uuidPlayer[1] + '\n Current IGN: ' + uuidPlayer[0],
                                inline=False)

        # Sends embed
        await ctx.send(embed=embedPage)

        # Prints log
        print(ctx.author.display_name + ' requested UUID!' + ". Done in %0.3fs." % (time() - t0))
        await confirmation.delete()

    ### XP leaderboard ###
    @commands.command(
        help="Shows current leaderboard of the XP competition and how much XP is left to gain to reach the goal",
        brief="Shows leaderboard of XP competition"
    )
    async def xpcomp(self, ctx):

        # Confirmation of start
        confirmation = await ctx.channel.send('Request received, generating...')
        t0 = time()

        # Load master list
        masterList = gen.mongtodf(mongUser, mongPass, 'xpcomp', 'masterList')

        # Pull current members of Nerfuria
        URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"
        fullGuildData = gen.requestget(URL)
        currentdf = xpcomp.extractmembers(fullGuildData)

        # Initialize final dataframe
        leaderboard = pd.DataFrame(columns=['Name', 'XP', 'Prestige'])

        # Compare lists
        for row in currentdf.itertuples(index=False):

            if row.uuid in masterList.uuid.values:
                ind = masterList.set_index('uuid').index.get_loc(row.uuid)
                xpCol = masterList['contributed']
                xp1 = xpCol[ind]
            else:
                xp1 = 0

            # Generating xp total
            name = row.name
            xp2 = row.contributed
            xpTotal = xp2 - xp1

            # Calculate Prestiges
            prestStr = xpcomp.prestCalc(xpTotal)

            leaderboard = leaderboard.append({'Name': name, 'XP': xpTotal, 'Prestige': prestStr}, ignore_index=True)

        # Setting leaderboards
        leaderboardMain = leaderboard.sort_values(by=['XP'], ascending=False, ignore_index=True)

        # Splits up into individual thresholds
        [leaderboardChamp, leaderboardHero, leaderboardVIPp, leaderboardVIP, leaderboardRest, leaderboardZero] = xpcomp.leaderboardSplit(leaderboardMain)

        # Gets title info for embed
        titleInfo = gen.mongtodf(mongUser, mongPass, "xpcomp", "titleInfo")
        titleInfo = titleInfo.sort_values(by=['index']).reset_index()

        # Get all guild leaderboard data
        allGuildData = gen.requestget('https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime')
        allGuildData = allGuildData.get('data')
        guilddf = pd.DataFrame(allGuildData)

        # Separate out Nia's xp level
        niaInfo = xpcomp.extractxpandlvl('Nerfuria', guilddf)

        # Calculate xp data
        xpdata = {'level': [95, 96, 97, 98, 99],
                  'xp': [77843189235, 89520186224, 102948810556, 118391818001, 136162150806]}
        xp_df = pd.DataFrame(xpdata)

        xpTotal = 0
        xpGrinded = 0
        for row in xp_df.itertuples(index=False):
            xpTotal += row.xp
            if row.level == niaInfo['lvl']:
                xpGrinded += niaInfo['xp']
            elif row.level < niaInfo['lvl']:
                xpGrinded += row.xp
        xpRemaining = xpTotal - xpGrinded

        # Embed Initialization
        page = 0
        embedPage = [0]

        # Generating embed body
        for row in titleInfo.itertuples(index=False):
            string = ''
            lb = eval(row.rank)

            # Looks for empty categories
            if lb.empty:
                embedPage[page] = discord.Embed(title=f"**ლ(ಠ益ಠლ) | *__Nerfurian XP Rankings__* | 💪 (•︡益︠•) 👊**", color=0x856c46)
                embedPage[page].set_footer(text='Requested by: ' + discord.utils.escape_markdown(ctx.author.display_name) + '')
                embedPage[page].add_field(name='***~--==__Estimated XP Remaining__==--~***',
                                value='`' + "{:,}".format(xpRemaining) + ' XP Left`',
                                inline=False)
                string = string + '> No one here yet!'
                embedPage[page].add_field(name=row.title2,
                                          value=string,
                                          inline=False)
                page += 1
                embedPage.extend(str(page))

            # Splits up data into 15 entry-long embed pages
            else:
                intPage = page
                reqPage = math.ceil(len(lb.index) / 15)
                ind = 0

                while page < (reqPage + intPage):
                    k = 0
                    while ind < reqPage:
                        j = 0
                        string = ''
                        while j <= 14:
                            j += 1
                            if k >= len(lb.index):
                                break
                            else:
                                if lb.iloc[k, 1] != 0:
                                    string = string + '> ' + row.title1 + lb.iloc[k, 0] + row.title3 + '\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + lb.iloc[k, 2] + '\n\n'
                                    k += 1
                                else:
                                    k += 1

                            if string:
                                embedPage[page] = discord.Embed(
                                    title=f"**ლ(ಠ益ಠლ) | *__Nerfurian XP Rankings__* | 💪 (•︡益︠•) 👊**", color=0x856c46)
                                embedPage[page].set_footer(
                                    text='Requested by: ' + discord.utils.escape_markdown(ctx.author.display_name) + '')
                                embedPage[page].add_field(name='***~--==__Estimated XP Remaining__==--~***',
                                                          value='`' + "{:,}".format(xpRemaining) + ' XP Left`',
                                                          inline=False)
                                embedPage[page].add_field(name=row.title2,
                                                          value=string,
                                                          inline=False)
                        if ind >= reqPage:
                            break
                        else:
                            ind += 1
                            page += 1
                            embedPage.extend(str(page))

        # Prints log
        print(ctx.author.display_name + ' requested XP leaderboard!' + ". Done in %0.3fs." % (time() - t0))
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
                if i < (page - 1):
                    i += 1
                    await message.edit(embed=embedPage[i])
            elif str(reaction) == '⏭':
                i = (page - 1)
                await message.edit(embed=embedPage[i])

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
            except:
                break

        await message.clear_reactions()

    ### Individual XP Rank ###
    @commands.command(
        help="Shows XP competition leaderboard ranking of specified player",
        brief="Shows individual ranking of a player"
    )
    async def xprank(self, ctx, *, ign):

        # Confirmation of start
        confirmation = await ctx.channel.send('Request received, generating...')
        t0 = time()

        # Load master list
        masterList = gen.mongtodf(mongUser, mongPass, 'xpcomp', 'masterList')

        # Pull current members of Nerfuria
        URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"
        fullGuildData = gen.requestget(URL)
        currentdf = xpcomp.extractmembers(fullGuildData)

        # Converts ign to uuid
        uuidPlayer = xpcomp.uuidfinder(ign)

        # Initializes embed item
        embedPage = discord.Embed(title=f"**| *__Personal Nerfurian XP Ranking__* |**", color=0x856c46)
        embedPage.set_footer(text='Requested by: ' + discord.utils.escape_markdown(ctx.author.display_name) + '')

        # If player ign doesn't exist
        if uuidPlayer[1] == "Error":
            embedPage.add_field(name='***ERROR***',
                                value='Specified player: ' + ign + ' does not exist!',
                                inline=False)

        else:
            # If player is in guild
            if uuidPlayer[1] in currentdf.uuid.values:

                # Finds initial XP score of player
                if uuidPlayer[1] in masterList.uuid.values:
                    ind = masterList.set_index('uuid').index.get_loc(uuidPlayer[1])
                    xpCol = masterList['contributed']
                    xp1 = xpCol[ind]
                else:
                    xp1 = 0

                # Gets exact name and second XP score of player
                ind = currentdf.set_index('uuid').index.get_loc(uuidPlayer[1])
                nameCol = currentdf['name']
                name = nameCol[ind]
                contributedCol = currentdf['contributed']
                xp2 = contributedCol[ind]

                # Finds XP total
                xpTotal = xp2 - xp1

                # Calculate Prestieges
                prestStr = xpcomp.prestCalc(xpTotal)

                # Creates main leaderboard and splits up into individual thresholds
                leaderboardMain = pd.DataFrame(columns=['Name', 'XP', 'Prestige'])
                leaderboardMain = leaderboardMain.append({'Name': name, 'XP': xpTotal, 'Prestige': prestStr}, ignore_index=True)
                [leaderboardChamp, leaderboardHero, leaderboardVIPp, leaderboardVIP, leaderboardRest, leaderboardZero] = xpcomp.leaderboardSplit(leaderboardMain)

                # Gets title info for embed
                titleInfo = gen.mongtodf(mongUser, mongPass, "xpcomp", "titleInfo")
                titleInfo = titleInfo.sort_values(by=['index']).reset_index()

                # Finding threshold of player
                for row in titleInfo.itertuples(index=False):
                    k = 0
                    lb = eval(row.rank)

                    # Looks for empty categories
                    if lb.empty:
                        k += 1
                        continue

                    # Generating value field
                    else:
                        embedPage.add_field(name=row.title2,
                                            value='> ' + row.title1 + lb.iloc[k, 0] + row.title3 + '\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + lb.iloc[k, 2],
                                            inline=False)
                        k += 1

                lb = leaderboardZero
                if not lb.empty:
                    embedPage.add_field(name="**__Not Reached a Threshold Yet__**",
                                        value='> ' + "**" + lb.iloc[
                                            0, 0] + "**" + '\n> XP: ' + "{:,}".format(lb.iloc[0, 1]) + lb.iloc[
                                                  0, 2],
                                        inline=False)
                    k += 1


            # If player is not in guild
            else:
                embedPage.add_field(name='***ERROR***',
                                    value='Specified player: ' + ign + ' is not in the guild!',
                                    inline=False)

        # Sends embed
        await ctx.send(embed=embedPage)

        # Prints log
        print(ctx.author.display_name + ' requested XP rank!' + ". Done in %0.3fs." % (time() - t0))
        await confirmation.delete()

    ### XP Redemption ###
    @commands.command(
        help="Let's Aerrihn update a player's redeemed XP amounts (Only usable by Aerrihn and Shoefarts",
        brief="Updates player XP redeemed amounts"
    )
    async def xpredeem(self, ctx, action, ign, redeemedXP):

        # Checks if user is Shoefarts or Aerrihn (Admin)
        if (ctx.author.id == 214554775956619264 or ctx.author.id == 278107914043129867):

            # Checks if action is recognized
            if (action == "add" or action == "subtract" or action == "reset"):

                # Checks if redeemedXP is int
                try:
                    redeemedXP = int(redeemedXP)

                # Not an int
                except ValueError:
                    await ctx.channel.send('Invalid XP amount! Final input must be a number.')

                # Is an int
                else:

                    # Checks if ign is valid
                    uuidPlayer = xpcomp.uuidfinder(ign)
                    if uuidPlayer[1] != "Error":

                        # Load master list
                        masterList = gen.mongtodf(mongUser, mongPass, 'xpcomp', 'masterList')

                        # Pull current members of Nerfuria
                        URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"
                        fullGuildData = gen.requestget(URL)
                        currentdf = xpcomp.extractmembers(fullGuildData)

                        # If player is in guild
                        if uuidPlayer[1] in currentdf.uuid.values:

                            # Finds initial XP score of player
                            if uuidPlayer[1] in masterList.uuid.values:
                                ind = masterList.set_index('uuid').index.get_loc(uuidPlayer[1])
                                xpCol = masterList['contributed']
                                xp1 = xpCol[ind]
                            else:
                                xp1 = 0

                            # Gets exact name and second XP score of player
                            ind = currentdf.set_index('uuid').index.get_loc(uuidPlayer[1])
                            nameCol = currentdf['name']
                            name = nameCol[ind]
                            contributedCol = currentdf['contributed']
                            xp2 = contributedCol[ind]

                            # Finds XP total
                            xpTotal = xp2 - xp1

                        # If player not in guild
                        else:
                            await ctx.channel.send('Player is not in the guild!')

                    # IGN not valid
                    else:
                        await ctx.channel.send('Invalid IGN! Check your spelling.')

            # Action not recognized
            else:
                await ctx.channel.send('Action not recognized! Available actions: add, subtract, reset')

        # User is not Aerrihn or Shoefarts
        else:
            await ctx.channel.send('Only Aerrihn can update the XP redeemed amounts!')


    ### Sets Initial XP for Leaderboard Calculation ###
    @commands.command(
        help="Resets XP leaderboard by updating the masterlist with the most recent copy of the API (Only usable by Shoe)",
        brief="Resets XP leaderboard (Only usable by Shoe)"
    )
    async def xpinit(self, ctx):

        # Checks if user is Shoefarts (Admin)
        if ctx.author.id == 214554775956619264:

            # Confirmation of overwrite
            confirm = await ctx.channel.send('You are trying to overwrite the initial XP state, continue?')
            await confirm.add_reaction('👍')
            await confirm.add_reaction('👎')

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎')

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)

            # If user fails to respond in time
            except asyncio.TimeoutError:
                print(ctx.author.display_name + ' timed out XP state overwrite attempt!')
                timeout = await ctx.channel.send('Timeout reached, Initial XP state overwrite canceled')
                await confirm.delete()

            else:

                # If user declines XP leaderboard overwrite
                if reaction.emoji == '👎':
                    print(ctx.author.display_name + ' cancelled XP state overwrite!')
                    cancel = await ctx.channel.send('Initial XP state overwrite canceled')
                    await confirm.delete()

                # If user approves XP leaderboard overwrite
                elif reaction.emoji == '👍':
                    loading = await ctx.channel.send('Grabbing state...')

                    URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"
                    fullGuildData = gen.requestget(URL)
                    masterdf = xpcomp.extractmembers(fullGuildData)

                    gen.dftomong(mongUser, mongPass, 'xpcomp', 'masterList', masterdf, True)

                    print(ctx.author.display_name + ' overwrote initial XP state!')
                    await ctx.channel.send('Initial XP state grabbed!')
                    await confirm.delete()
                    await loading.delete()

        else:
            await ctx.channel.send('Only Shoefarts can update the XP leaderboard!')


# Setup call
def setup(bot):
    bot.add_cog(xpCompSuite(bot))