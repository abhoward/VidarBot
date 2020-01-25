import discord
from discord.ext import commands
import traceback

import nest_asyncio

nest_asyncio.apply()

token = 'NjY3MjgwODQ0NzgzNjE2MDAx.XiAcew.KiJz_-KeONfRW782ai09y1rcbUs'
guild_name = 'The Shiny Den'

bot = commands.Bot(command_prefix = 'v!')

client = discord.Client()

# @client.event
# async def on_ready():
#     print('Logged in as {}'.format(client.user))
    
# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#     if message.content.startswith('$hello'):
#         await message.channel.send('Hi!')
        
# @client.event
# async def on_ready():
#     guild = discord.utils.find(lambda g: g.name == guild_name, client.guilds)
            
#     print('{} (id: {})'.format(guild.name, guild.id))
    
#     members = '\n -'.join([member.display_name for member in guild.members])
#     print('Guild Members:\n - {}'.format(members))
    
@bot.event
async def on_command_error(ctx, error):
    # if isinstance(error, commands.errors.CommandNotFound):
    #     await ctx.send(error)
    # elif isinstance(error, commands.errors.BadArgument):
    await ctx.send(error)
    
    raise error

@bot.command(name = 'assign', help = 'Assigns a role to the user.')
@commands.has_role('Administrator')
async def on_message(ctx, user: discord.Member, role_to_assign: discord.Role):
    user_list = []
    for member in ctx.guild.members:
        if member.display_name == user.display_name: 
            user_list.append(user)
            
    if len(user_list) > 1:
        await ctx.send("{} matches more than one name in the server, please be more specific or assign the role manually.".format(user_list[0].display_name))
    else:
        await user.add_roles(role_to_assign)
        
    del user_list

bot.run(token)