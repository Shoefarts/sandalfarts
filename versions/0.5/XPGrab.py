import discord
import os
import requests
import ast
import pandas as pd
import math

# Requests Setup

# Discord Bot
client = discord.Client()

# Bot Initialization
@client.event
async def on_ready():
    print('Daddy {0.user} is here'.format(client))

# Event Tracker
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Leaderboard
    if message.content.startswith(':shoexp'):
        #Ravioli ravioli, give me the formuoli

        # Load master list
        masterdf = pd.read_csv('masterlist.csv')

        # Pull current API list
        URL = "https://api.wynncraft.com/public_api.php?action=guildStats&command=Nerfuria"

        r = requests.get(URL)
        byte_str = r.content
        dict_str = byte_str.decode("UTF-8")
        fullGuildData = ast.literal_eval(dict_str)

        members = fullGuildData.get('members')

        remove = ('rank', 'joined', 'joinedFriendly')
        for entry in members:
            for key in remove:
                entry.pop(key, None)

        currentdf = pd.DataFrame.from_dict(members)

        # Initialize final dataframe
        leaderboard = pd.DataFrame(columns=['Name', 'XP'])

        # Compare lists
        for row in currentdf.itertuples(index=False):

            if row.uuid in masterdf.uuid.values:
                ind = masterdf.set_index('uuid').index.get_loc(row.uuid)
                xpCol = masterdf['contributed']
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

        leaderboardChamp = leaderboardMain[leaderboardMain.XP >= 49000000000]
        leaderboardHero = leaderboardMain[(leaderboardMain['XP'] >= 24000000000) & (leaderboardMain['XP'] < 49000000000)]
        leaderboardVIPp = leaderboardMain[(leaderboardMain['XP'] >= 8000000000) & (leaderboardMain['XP'] < 24000000000)]
        leaderboardVIP = leaderboardMain[(leaderboardMain['XP'] >= 2000000000) & (leaderboardMain['XP'] < 8000000000)]
        leaderboardRest = leaderboardMain[leaderboardMain.XP < 2000000000]

        # Generating output message
        embed = discord.Embed(title=f"**ლ(ಠ益ಠლ) | *__Nerfurian XP Rankings__* | 💪 (•︡益︠•) 👊**", color=0x856c46)

        # Champions field
        string = ''
        lb = leaderboardChamp
        if lb.empty:
            string = string + 'No one here yet!'
            embed.add_field(name=f'**👑 __Champions Threshold__ 👑**',
                            value=string,
                            inline=False)
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
                        string = string + '> ▁ ▂ ▄ ▅ ▆ ▇ █**`' + lb.iloc[k, 0] + '`**█ ▇ ▆ ▅ ▄ ▂ ▁\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                        k += 1
                embed.add_field(name=f'**👑 __Champions Threshold__ 👑**',
                                value=string,
                                inline=False)
                i += 1

        # Hero field
        string = ''
        lb = leaderboardHero
        if lb.empty:
            string = string + 'No one here yet!'
            embed.add_field(name=f'**🔥 __Heros Threshold__ 🔥**',
                            value=string,
                            inline=False)
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
                        string = string + '> —(••÷[**' + lb.iloc[k, 0] + '**]÷••)—\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                        k += 1
                embed.add_field(name=f'**🔥 __Heros Threshold__ 🔥**',
                                value=string,
                                inline=False)
                i += 1

        # VIP+ field
        string = ''
        lb = leaderboardVIPp
        if lb.empty:
            string = string + 'No one here yet!'
            embed.add_field(name=f'**💪 __VIP Threshold__ 💪**',
                            value=string,
                            inline=False)
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
                        string = string + '> **✿' + lb.iloc[k, 0] + '✿**\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                        k += 1
                embed.add_field(name=f'**💪 __VIP+ Threshold__ 💪**',
                                value=string,
                                inline=False)
                i += 1

        # VIP field
        string = ''
        lb = leaderboardVIP
        if lb.empty:
            string = string + 'No one here yet!'
            embed.add_field(name=f'**😎 __VIP Threshold__ 😎**',
                            value=string,
                            inline=False)
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
                        string = string + '> **' + lb.iloc[k, 0] + '**\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                        k += 1
                embed.add_field(name=f'**😎 __VIP Threshold__ 😎**',
                                value=string,
                                inline=False)
                i += 1

        # The Rest field
        string = ''
        lb = leaderboardRest
        if lb.empty:
            string = string + 'No one here yet!'
            embed.add_field(name=f'**__Not Reached a Threshold Yet__**',
                            value=string,
                            inline=False)
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
                            string = string + '> **' + lb.iloc[k, 0] + '**\n> XP: ' + "{:,}".format(lb.iloc[k, 1]) + '\n'
                            k += 1
                        else:
                            k += 1
                if string:
                    embed.add_field(name=f'**__Not Reached a Threshold Yet__**',
                                    value=string,
                                    inline=False)
                i += 1

        # Sends Message
        await message.channel.send(embed=embed)

client.run(os.getenv('TOKEN'))