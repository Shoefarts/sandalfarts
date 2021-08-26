import discord
from discord.ext import commands
import asyncio

# the clowntown manifesto
manifest = []
botids = [866897574938279966, 849490658409316353]

# Contains all commands related to the marvelous Clown Town Express
class clownTownExpress(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### clown down ###
    @commands.Cog.listener("on_message")
    async def honk(self, ctx):

        # honks at clowns
        if ctx.author.id in manifest:
            if ctx.author.id not in botids:
                await ctx.add_reaction('🤡')

    ### Clown town party ###
    @commands.command(
        help="**sda**adkahjpqlx_*sasdav_**lnlabnnziqwe`kjkj`nc",
        brief="oisdoidm`jkgkhkhk*bksdfjnb_`kbs"
    )
    async def clownparty(self, ctx):

        # checks if the train conductor is an admin
        if discord.utils.get(ctx.author.roles, name="Admin"):
            # selling tickets to passengers
            embed = discord.Embed(title=f"Who wants to go to Clown Town? 🚅", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"The train\'s leavin\' in one minute, grab a ticket if you wanna get on!\"',
                            inline=False)
            tickets = await ctx.channel.send(embed=embed, delete_after=65)
            await tickets.add_reaction('🎟️')
            await asyncio.sleep(60)
            getManifest = await ctx.channel.fetch_message(tickets.id)
            clowns = await getManifest.reactions[0].users().flatten()
            # figuring out passenger manifest
            for clown in clowns:
                if clown.id in (manifest or botids):
                    continue
                else:
                    manifest.append(clown.id)
            # choo choo
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Choo choo...\"',
                            inline=False)
            await ctx.channel.send(embed=embed, delete_after=5)
            await ctx.channel.send('Type `:sh getmeoffthistrain` to escape...')
            print(ctx.author.display_name + ' called the train!')
        else:
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"You do you think you are? you don\'t have the power to call this train...\"',
                            inline=False)
            await ctx.channel.send(embed=embed, delete_after=5)


    ### emergency entrance ###
    @commands.command(
        help="owemc1093fmoqsdl*kldjf**oj3m2*o_s_1200cmso4ns",
        brief="anfqej3k_asfrbo_~~jkjk9~~~mao"
    )
    async def takemetoclowntown(self, ctx):

        # getting on but off the train
        if ctx.author.id not in manifest:
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Well if you really want to get on...\"',
                            inline=False)
            response = await ctx.channel.send(embed=embed)
            await response.add_reaction('🎟️')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '🎟️'

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                print(ctx.author.display_name + ' chose not to get on the train!')
                embed = discord.Embed(title=f"...", color=0xFF6363)
                embed.add_field(name='**🤹 ‍Ticketmaster:**',
                                value='> \"What a waste of time...\"',
                                inline=False)
                await ctx.channel.send(embed=embed, delete_after=5)

            else:
                manifest.append(ctx.author.id)
                embed = discord.Embed(title=f"...", color=0xFF6363)
                embed.add_field(name='**🤹 ‍Ticketmaster:**',
                                value='> \"Choo choo...\"',
                                inline=False)
                print(ctx.author.display_name + ' got on the train!')
                await ctx.channel.send(embed=embed, delete_after=5)
                await ctx.channel.send('Type `:sh getmeoffthistrain` to escape...')
            await response.delete()
        # getting on but on the train
        else:
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"Sit back down! You\'re already on the train...\"',
                            inline=False)
            await ctx.channel.send(embed=embed, delete_after=5)
            await ctx.channel.send('Type `:sh getmeoffthistrain` to escape...')

    ### emergency exit ###
    @commands.command(
        help="4nlnvls*asflai*cwo__dskjd~~fa**i**~~20mf9dkq__qsonvbeos",
        brief="akgwkjns*sdfsfo*012jfog"
    )
    async def getmeoffthistrain(self, ctx):

        # getting off but on the train
        if ctx.author.id in manifest:
            manifest.remove(ctx.author.id)
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"You\'ll be back...\"',
                            inline=False)
            print(ctx.author.display_name + ' got off the train!')
        # getting off but not on the train
        else:
            embed = discord.Embed(title=f"...", color=0xFF6363)
            embed.add_field(name='**🤹 ‍Ticketmaster:**',
                            value='> \"You\'re not on the train, get out of my sight...\"',
                            inline=False)
        await ctx.channel.send(embed=embed, delete_after=5)


# Setup call
def setup(bot):
    bot.add_cog(clownTownExpress(bot))