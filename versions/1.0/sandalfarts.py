# Requests Setup
import discord
from discord.ext import commands, tasks
import os
import pandas as pd
import math
import asyncio
import pymongo
from packages.fart import fart

# Bot mode
discMode = 'proto'

# Discord Bot
client = discord.Client()

# MongoDB Login
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')
mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')

# Clowntown Manifest Initialization
manifest = []
botids = [866897574938279966, 849490658409316353]
manifest.extend(botids)

# Bot Initialization
@client.event
async def on_ready():
    print('Daddy {0.user} is here'.format(client))

# Event Tracker
@client.event
async def on_message(message):
    if message.author == client.user:
        return


    ### Sets Initial XP for Leaderboard Calculation ###
    elif message.author.id == 214554775956619264 and message.content == ':sh xpinit':

        # Confirmation of overwrite
        confirm = await message.channel.send('You are trying to overwrite the initial XP state, continue?')
        await confirm.add_reaction('👍')
        await confirm.add_reaction('👎')

        def check(reaction, user):
            return user == message.author and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎')
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            print(message.author.display_name + ' timed out XP state overwrite attempt!')
            timeout = await message.channel.send('Timeout reached, Initial XP state overwrite canceled')
            await confirm.delete()

        else:
            if reaction.emoji == '👎':
                print(message.author.display_name + ' cancelled XP state overwrite!')
                cancel = await message.channel.send('Initial XP state overwrite canceled')
                await confirm.delete()

            elif reaction.emoji == '👍':
                loading = await message.channel.send('Grabbing state...')

                URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"
                fullGuildData = fart.requestget(URL)
                masterdf = fart.extractmembers(fullGuildData)

                fart.dftomong(mongUser, mongPass, 'xpcomp', 'masterList', masterdf, True)

                print(message.author.display_name + ' overwrote initial XP state!')
                await message.channel.send('Initial XP state grabbed!')
                await confirm.delete()
                await loading.delete()


    ### XP Leaderboard ###
    elif message.content == ':sh xpcomp':

        confirmation = await message.channel.send('Request received, generating...')

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
        embed.set_footer(text="Requested by: {}".format(message.author.display_name))

        # Gets title info for embed
        titleInfo = fart.mongtodf(mongUser, mongPass, "xpcomp", "titleInfo")
        titleInfo = titleInfo.sort_values(by=['index']).reset_index()

        # Get all guild leaderboard data
        allGuildData = fart.requestget('https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime')
        allGuildData = allGuildData.get('data')
        guilddf = pd.DataFrame(allGuildData)

        # Separate out Nia's xp level
        niaInfo = fart.extractxpandlvl('Nerfuria', guilddf)

        # Calculate xp data
        xpdata = {'level': [81, 82, 83, 84, 85, 86, 87, 88, 89],
                  'xp': [11001668175, 12651938401, 14549749161, 16732231535, 19242086266, 22128419206, 25447702087, 29264877400, 33654629009]}
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
        embed.add_field(name='***~--==__XP Remaining__==--~***',
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
                                string = string + '> ' + row.title1 + lb.iloc[k, 0] + row.title3 + '\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                                k += 1
                            else:
                                k += 1
                    if string:
                        embed.add_field(name=row.title2,
                                        value=string,
                                        inline=False)
                    i += 1

        # Sends Message
        print(message.author.display_name + ' requested XP leaderboard!')
        await message.channel.send(embed=embed)
        await confirmation.delete()


    ### clown town express ***
    elif message.content == ':sh clowntown':
        # checks if the train conductor is an admin
        if discord.utils.get(message.author.roles, name="Admin"):
            # selling tickets to passengers
            embed = discord.Embed(title=f"Who wants to go to Clown Town? 🚅", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"The train\'s leavin\' in one minute, grab a ticket if you wanna get on!\"',
                            inline=False)
            tickets = await message.channel.send(embed=embed)
            await tickets.add_reaction('🎟️')
            await asyncio.sleep(60)
            getManifest = await message.channel.fetch_message(tickets.id)
            clowns = await getManifest.reactions[0].users().flatten()
            # figuring out passenger manifest
            for clown in clowns:
                if clown.id in manifest:
                    continue
                else:
                    manifest.append(clown.id)
            await tickets.delete()
            # choo choo
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Choo choo...\"',
                            inline=False)
            confirmation = await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            await confirmation.delete()
            await message.channel.send('Type `:sh getmeoffthistrain` to escape...')
            print(message.author.display_name + ' called the train!')
    # emergency entrance
    elif message.content == ':sh takemetoclowntown':
        # getting on but off the train
        if message.author.id not in manifest:
            manifest.append(message.author.id)
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Well if you really want to get on...\"',
                            inline=False)
            response = await message.channel.send(embed=embed)
            await response.add_reaction('🎟️')

            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '🎟️'

            try:
                reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                print(message.author.display_name + ' chose not to get on the train!')
                await response.delete()
                embed = discord.Embed(title=f"...", color=0xFF6363)
                embed.add_field(name='**🤹 ‍Ticketmaster:**',
                                value='> \"What a waste of time...\"',
                                inline=False)
                timeout = await message.channel.send(embed=embed)
                await asyncio.sleep(5)
                await timeout.delete()
            await response.delete()
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Choo choo...\"',
                            inline=False)
            print(message.author.display_name + ' got on the train!')
        # getting on but on the train
        else:
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Sit back down! You\'re already on the train...\"',
                            inline=False)
        confirmation = await message.channel.send(embed=embed)
        await message.channel.send('Type `:sh getmeoffthistrain` to escape...')
        await asyncio.sleep(5)
        await confirmation.delete()
    # emergency exit
    elif message.content == ':sh getmeoffthistrain':
        # getting off but on the train
        if message.author.id in manifest:
            manifest.remove(message.author.id)
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"You\'ll be back...\"',
                            inline=False)
            print(message.author.display_name + ' got off the train!')
        # getting off but not on the train
        else:
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"You\'re not on the train, get out of my sight...\"',
                            inline=False)
        response = await message.channel.send(embed=embed)
        await asyncio.sleep(5)
        await response.delete()
    # clown
    elif message.author.id in manifest:
        await message.add_reaction('🤡')

if discMode == 'sandals':
    # For Sandals
    client.run(os.getenv('TOKEN'))
elif discMode == 'proto':
    # For Proto
    client.run(os.getenv('ProtoTOKEN'))