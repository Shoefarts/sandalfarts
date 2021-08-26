import discord
from discord.ext import commands
import sys
sys.path.append("..")
from packages.fart import fart
import os
import pandas as pd
import math
import asyncio

# Mongdb login credentials
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')

# Contains all commands related to XP competition
class xpCompSuite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### XP leaderboard ###
    @commands.command(
        help="Shows current leaderboard of the XP competition and how much XP is left to gain to reach the goal",
        brief="Shows leaderboard of XP competition"
    )
    async def xpcomp(self, ctx):

        confirmation = await ctx.channel.send('Request received, generating...')

        # Load master list
        masterList = fart.mongtodf(mongUser, mongPass, 'xpcomp', 'masterList')

        # Pull current members of Nerfuria
        URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"
        fullGuildData = fart.requestget(URL)
        currentdf = fart.extractmembers(fullGuildData)

        # Initialize final dataframe
        leaderboard = pd.DataFrame(columns=['Name', 'XP'])

        # Compare lists
        for row in currentdf.itertuples(index=False):

            if row.uuid in masterList.uuid.values:
                ind = masterList.set_index('uuid').index.get_loc(row.uuid)
                xpCol = masterList['contributed']
                xp1 = xpCol[ind]
            else:
                xp1 = 0

            # Generating leaderboard
            name = row.name
            xp2 = row.contributed
            xpTotal = xp2 - xp1
            leaderboard = leaderboard.append({'Name': name, 'XP': xpTotal}, ignore_index=True)

        # Setting leaderboards
        leaderboardMain = leaderboard.sort_values(by=['XP'], ascending=False, ignore_index=True)

        leaderboardChamp = leaderboardMain[leaderboardMain.XP >= 37000000000]
        leaderboardHero = leaderboardMain[(leaderboardMain.XP >= 18000000000) & (leaderboardMain.XP < 37000000000)]
        leaderboardVIPp = leaderboardMain[(leaderboardMain.XP >= 6000000000) & (leaderboardMain.XP < 18000000000)]
        leaderboardVIP = leaderboardMain[(leaderboardMain.XP >= 1500000000) & (leaderboardMain.XP < 6000000000)]
        leaderboardRest = leaderboardMain[leaderboardMain.XP < 1500000000]

        # Generating output message
        embed = discord.Embed(title=f"**ლ(ಠ益ಠლ) | *__Nerfurian XP Rankings__* | 💪 (•︡益︠•) 👊**", color=0x856c46)
        embed.set_footer(text='Requested by: ' + discord.utils.escape_markdown(ctx.author.display_name) + '')

        # Gets title info for embed
        titleInfo = fart.mongtodf(mongUser, mongPass, "xpcomp", "titleInfo")
        titleInfo = titleInfo.sort_values(by=['index']).reset_index()

        # Get all guild leaderboard data
        allGuildData = fart.requestget(
            'https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime')
        allGuildData = allGuildData.get('data')
        guilddf = pd.DataFrame(allGuildData)

        # Separate out Nia's xp level
        niaInfo = fart.extractxpandlvl('Nerfuria', guilddf)

        # Calculate xp data
        xpdata = {'level': [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93 ,94],
                  'xp': [11001668175, 12651938401, 14549749161, 16732231535, 19242086266, 22128419206, 25447702087,
                         29264877400, 33654629009, 38702507644, 44507883791, 51184066360, 58861676314, 67690927761]}
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
        embed.add_field(name='***~--==__Estimated XP Remaining__==--~***',
                        value='`' + "{:,}".format(xpRemaining) + ' XP Left`',
                        inline=False)

        # Generating embed body
        for row in titleInfo.itertuples(index=False):
            string = ''
            lb = eval(row.rank)

            # Looks for empty categories
            if lb.empty:
                string = string + '> No one here yet!'
                embed.add_field(name=row.title2,
                                value=string,
                                inline=False)

            # Generates filled categories and splits them into groups of 15, if able
            else:
                reqFields = math.ceil(len(lb.index) / 15)
                i = 1
                k = 0
                while i <= reqFields:
                    j = 0
                    string = ''
                    while j <= 14:
                        j += 1
                        if k >= len(lb.index):
                            break
                        else:
                            if lb.iloc[k, 1] != 0:
                                string = string + '> ' + row.title1 + lb.iloc[
                                    k, 0] + row.title3 + '\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                                k += 1
                            else:
                                k += 1
                    if string:
                        embed.add_field(name=row.title2,
                                        value=string,
                                        inline=False)
                    i += 1

        # Sends Message
        print(ctx.author.display_name + ' requested XP leaderboard!')
        await ctx.channel.send(embed=embed)
        await confirmation.delete()

    ### Sets Initial XP for Leaderboard Calculation ###
    @commands.command(
        help="Resets XP leaderboard by updating the masterlist with the most recent copy of the API (Only usable by Shoe)",
        brief="Resets XP leaderboard (Only usable by Shoe)"
    )
    async def xpinit(self, ctx):

        # Checks if user is Shoefarts
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
                    fullGuildData = fart.requestget(URL)
                    masterdf = fart.extractmembers(fullGuildData)

                    fart.dftomong(mongUser, mongPass, 'xpcomp', 'masterList', masterdf, True)

                    print(ctx.author.display_name + ' overwrote initial XP state!')
                    await ctx.channel.send('Initial XP state grabbed!')
                    await confirm.delete()
                    await loading.delete()

        else:
            await ctx.channel.send('Only Shoefarts can update the XP leaderboard!')


# Setup call
def setup(bot):
    bot.add_cog(xpCompSuite(bot))