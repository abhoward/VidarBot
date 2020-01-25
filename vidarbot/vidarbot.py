import discord
from discord.ext import commands

from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

prefix = '?'  # change this to whatever prefix you'd like
token = 'NjY3MjgwODQ0NzgzNjE2MDAx.XiAcew.KiJz_-KeONfRW782ai09y1rcbUs'

bot = commands.Bot(command_prefix=prefix)

# add roles that can use some commands
approved_roles = ['Administrator', 'Robot', 'Moderator']

# ids of the channels that the bot is listening to
channel_ids = [666368382219714570, 669973711503491134, 670322875894333484]

# needs to be updated every time the den is changed
available_pokemon = ['salandit', 'toxel', 'drapion', 'toxtricity', 'weezing', 'skuntank', 'salazzle', 'garbodor']

def is_approved():
    def predicate(ctx):
        author = ctx.author
        if author is ctx.guild.owner:
            return True
        if any(role.name in approved_roles for role in author.roles):
            return True
    return commands.check(predicate)

def is_channel(channel_ids):
    def predicate(ctx):
        return ctx.message.channel.id in channel_ids
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)

@bot.event
async def on_command_error(ctx, error):
    await ctx.author.send(f'Your command resulted in an error. Please review your command and try again or contact Alec for help.')
    
    raise error

class Queue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.qtoggle = False
        self.queue = []

        # add users who have special queue privileges
        self.approved_users = []
            
        # a history of users who have entered the queue
        self.queue_history = []

        # add users who have special queue privileges
        self.approved_users = []

    @is_channel(channel_ids)
    @commands.command(aliases = ['join'])
    async def add(self, ctx):
        ''': Add yourself to the queue!'''
        author = ctx.author
        if self.qtoggle:
            if author.id in self.approved_users: # if the user is approved
                self.queue.append(author.id)
                self.queue_history.append(author.id)
                await ctx.author.send('You have been added to the queue.')
            elif author.id not in self.queue_history: # if the user has never entered the queue
                self.queue.append(author.id)
                self.queue_history.append(author.id)
                await ctx.author.send('You have been added to the queue.')
            elif author.id not in self.queue: # if the user has already entered the queue once before
                await ctx.author.send('You have already joined this queue once.')
            else:
                await ctx.author.send('You are already in the queue.')
        else:
            await ctx.author.send('The queue is closed.')

    @is_channel(channel_ids)
    @commands.command()
    async def remove(self, ctx):
        ''': Remove yourself from the queue'''
        author = ctx.author
        if author.id in self.queue:
            self.queue.remove(author.id)
            self.queue_history.remove(author.id)
            await ctx.author.send('You have been removed from the queue.')
        else:
            await ctx.author.send('You are not in the queue.')

    @is_channel(channel_ids)
    @commands.command(aliases = ['queue'])
    async def view(self, ctx):
        ''': See who's up next!'''
        guild = ctx.guild
        message = ''
        for place, member_id in enumerate(self.queue):
            member = discord.utils.get(guild.members, id=member_id)
            message += f'**#{place+1}** : {member.display_name}\n'
        if message != '':
            await ctx.author.send(message)
        else:
            await ctx.author.send('Queue is empty')

    @is_channel(channel_ids)
    @commands.command()
    async def pos(self, ctx):
        ''': Check your position in the queue'''
        author = ctx.author
        if author.id in self.queue:
            _position = self.queue.index(author.id)+1
            await ctx.author.send(f'You are **#{_position}** in the queue.')
        else:
            await ctx.author.send(f'You are not in the queue, please use `{prefix}add` to add yourself to the queue.')

    @is_channel(channel_ids)
    @commands.command()
    async def move(self, ctx, position):
        ''': Move yourself down to a position supplied by the user'''
        author = ctx.author
        old_pos = int(self.queue.index(author.id)) + 1
        if position.isdigit():
            if author.id in self.queue:
                self.queue.insert(int(position), self.queue.pop(old_pos - 1))
                new_pos = int(self.queue.index(author.id)) + 1
                await ctx.author.send(f'You have been moved from {str(old_pos)} to {str(new_pos)}.')
            else:
                await ctx.author.send(f'You are not in the queue, please use `{prefix}add` to add yourself to the queue.')
        else:
            await ctx.author.send(f'You entered {position} instead of a positive integer. Please try again.')

    @is_channel(channel_ids)
    @commands.command()
    async def length(self, ctx):
        ''': Check the length of the queue'''
        if self.qtoggle:
            length = len(self.queue)
            await ctx.author.send(f'The queue is {length} members long.')
        else:
            await ctx.author.send('The queue is closed.')

    @is_approved()
    @commands.command()
    async def approve(self, ctx):
        ''': Adds a user to the approved users list.'''
        user = ctx.message.mentions[0]
        if user.id not in self.approved_users:
            self.approved_users.append(user.id)
            await ctx.send(f'{user.mention} has been added to the approved users list.')
        else:
            await ctx.send(f'{user.mention} is already in the approved users list.')

    @is_approved()
    @commands.command()
    async def unapprove(self, ctx):
        ''': Removes a user from the approved users list.'''
        user = ctx.message.mentions[0]
        if user.id in self.approved_users:
            self.approved_users.remove(user.id)
            await ctx.send(f'{user.mention} has been removed from the approved users list.')
        else: 
            await ctx.send(f'{user.mention} is not in the approved users list.')

    @is_approved()
    @commands.command()
    async def mremove(self, ctx):
        ''': Remove another member from the queue'''
        user = ctx.message.mentions[0]
        if user.id in self.queue:
            self.queue.remove(user.id)
            self.queue_history.remove(user.id)
            await ctx.author.send(f'{user.mention} has been removed from the queue.')
        else:
            await ctx.author.send(f'{user.mention} is not in the queue.')

    @is_approved()
    @commands.command(name='next')
    async def _next(self, ctx, raid_code):
        ''': Call the next member in the queue'''
        if len(self.queue) > 0:
            if len(raid_code) == 4 and raid_code.isdigit():
                member = discord.utils.get(ctx.guild.members, id=self.queue[0])
                await member.send(f"It's your turn to raid! Please make sure you add Alec's FC below.\nIf you cannot make it or you are having issues joining please inform Alec ASAP. If you are a no-show you will be skipped. Good luck and have fun!\n```Code: {raid_code} \nFC: 8119-6654-7598 (thall)```")
                await ctx.author.send(f"It is now {member.mention}'s turn to raid with the following code: `{raid_code}`")
                self.queue.remove(self.queue[0])
            else:
                await ctx.author.send(f'Your raid code of `{raid_code}`  is invalid. Please try again.')
        else:
            await ctx.author.send('Queue is empty.')

    @is_approved()
    @commands.command()
    async def clear(self, ctx):
        ''': Clears the queue'''
        self.queue = []
        await ctx.author.send('Queue has been cleared.')

    @is_approved()
    @commands.command()
    async def toggle(self, ctx):
        ''': Toggles the queue'''
        self.qtoggle = not self.qtoggle
        if self.qtoggle:
            state = 'OPEN'
        else:
            state = 'CLOSED'
        await ctx.send(f'Queue is now {state}.')

    @is_approved()
    @commands.command()
    async def export(self, ctx, file_name):
        ''': Exports the current queue to a .csv file'''
        usernames = [ctx.guild.get_member(i) for i in self.queue_history]
        file_path = Path(f'queue_logs/{file_name}.csv')
        df = pd.DataFrame({'user': usernames})
        df.to_csv(file_path)
        await ctx.author.send(f'A .csv file has been saved to `{file_path}`.')

class rQueue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queue = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])
        self.qtoggle = False

        # a history of users who have entered the queue
        self.queue_history = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])

        # add users who have special queue privileges
        self.approved_users = []

        # dataframe that we'll use later to group by pokemon
        self.grouped_queue = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])

    @is_channel(channel_ids)
    @commands.command()
    async def radd(self, ctx, pokemon):
        ''': Add yourself to the queue with the pokemon that you want to catch'''
        author = ctx.author
        if self.qtoggle:
            if pokemon.lower() in available_pokemon:
                if author.id in self.approved_users: # if the user is approved
                    self.queue = self.queue.append({'user_id': author.id, 'username': author, 'pokemon': pokemon.lower(), 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}, ignore_index = True)
                    self.queue_history = self.queue_history.append({'user_id': author.id, 'username': author, 'pokemon': pokemon.lower(), 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}, ignore_index = True)
                    await ctx.author.send('You have been added to the queue.')
                elif author.id not in self.queue_history['user_id'].tolist(): # if the user has never entered the queue
                    self.queue = self.queue.append({'user_id': author.id, 'username': author, 'pokemon': pokemon.lower(), 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}, ignore_index = True)
                    self.queue_history = self.queue_history.append({'user_id': author.id, 'username': author, 'pokemon': pokemon.lower(), 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}, ignore_index = True)
                    await ctx.author.send('You have been added to the queue.')
                elif author.id not in self.queue['user_id'].tolist(): # if the user has already entered the queue once before
                    await ctx.author.send('You have already joined this queue once.')
                else:
                    await ctx.author.send('You are already in the queue.')
            else: 
                await ctx.author.send(f'{pokemon} is an invalid pokemon. Please ensure you enter one of the following pokemon: \n' + ', '.join(available_pokemon))
        else:
            await ctx.author.send('The queue is closed.')

    @is_channel(channel_ids)
    @commands.command()
    async def rremove(self, ctx):
        ''': Remove yourself entirely from the queue'''
        author = ctx.author
        if author.id not in self.queue['user_id'].tolist() and author.id not in self.grouped_queue['user_id'].tolist():
            await ctx.author.send('You are not in the queue.')
        else:   
            if author.id in self.grouped_queue['user_id'].tolist():
                self.grouped_queue = self.grouped_queue[self.grouped_queue['user_id'] != author.id].reset_index(drop = True)
                self.queue_history = self.queue_history[self.queue_history['user_id'] != author.id].reset_index(drop = True)
                await ctx.author.send('You have been removed from the group queue.')

            # want to do both above and below statement, hence why no else statement
            if author.id in self.queue['user_id'].tolist():
                self.queue = self.queue[self.queue['user_id'] != author.id].reset_index(drop = True)
                self.queue_history = self.queue_history[self.queue_history['user_id'] != author.id].reset_index(drop = True)
                await ctx.author.send('You have been removed from the overall queue.')

    @is_channel(channel_ids)
    @commands.command()
    async def rview(self, ctx, _type):
        ''': See who's up next!'''
        guild = ctx.guild
        message = ''

        if _type.lower() == 'group':
            if not self.grouped_queue.empty:
                for place, values in enumerate(self.grouped_queue[['user_id', 'pokemon']].values):
                    member_id = values[0]
                    pokemon = values[1]

                    member = discord.utils.get(guild.members, id=member_id)
                    message += f'**#{place+1}** : {member.display_name} - {pokemon}\n'
                if message != '':
                    await ctx.author.send(message)
            else:
                await ctx.author.send('The group queue is empty.')
        elif _type.lower() == 'overall':
            if not self.queue.empty:
                for place, values in enumerate(self.queue[['user_id', 'pokemon']].values):
                    member_id = values[0]
                    pokemon = values[1]

                    member = discord.utils.get(guild.members, id=member_id)
                    message += f'**#{place+1}** : {member.display_name} - {pokemon}\n'
                if message != '':
                    await ctx.author.send(message)
            else:
                await ctx.author.send('The overall queue is empty.')
        else:
            await ctx.author.send(f'{_type} is not a valid queue type. Please enter either "overall" or "group" as a queue type.')

    @is_channel(channel_ids)
    @commands.command()
    async def rpos(self, ctx):
        ''': Check your position in the queue'''
        author = ctx.author
        if author.id in self.grouped_queue['user_id'].tolist():
            _position = self.grouped_queue[self.grouped_queue['user_id'] == author.id].index[0] + 1
            await ctx.author.send(f'You are **#{_position}** in the queue.')
        elif author.id in self.queue['user_id'].tolist():
            _position = self.queue[self.queue['user_id'] == author.id].index[0] + 1
            self.queue[self.queue['user_id'] == author.id].index[0]
            await ctx.author.send(f'You are **#{_position}** in the queue.')
        else:
            await ctx.author.send(f'You are not in the queue, please use `{prefix}add` to add yourself to the queue.')

    @is_channel(channel_ids)
    @commands.command()
    async def rmove(self, ctx, position):
        ''': Move yourself down to a position supplied by the user'''
        author = ctx.author
        if position.isdigit():
            position = int(position)
            if author.id in self.grouped_queue['user_id'].tolist():
                old_pos = np.where(self.grouped_queue['user_id'] == author.id)[0][0]
                row_to_insert = self.grouped_queue.iloc[[old_pos], :]
                self.grouped_queue.drop([old_pos], inplace = True)
                self.grouped_queue = pd.concat([self.grouped_queue.iloc[:position - 1], row_to_insert, self.grouped_queue.iloc[position - 1:]]).reset_index(drop=True)
                new_pos = min(position, len(self.grouped_queue))
                await ctx.author.send(f'You have been moved from {str(old_pos + 1)} to {str(new_pos)}.')
            elif author.id in self.queue['user_id'].tolist():
                old_pos = np.where(self.queue['user_id'] == author.id)[0][0]
                row_to_insert = self.queue.iloc[[old_pos], :]
                self.queue.drop([old_pos], inplace = True)
                self.queue = pd.concat([self.queue.iloc[:position - 1], row_to_insert, self.queue.iloc[position - 1:]]).reset_index(drop=True)
                new_pos = min(position, len(self.queue))
                await ctx.author.send(f'You have been moved from {str(old_pos + 1)} to {str(new_pos)}.')
            else:
                await ctx.author.send(f'You are not in the queue, please use `{prefix}add` to add yourself to the queue.')
        else:
            await ctx.author.send(f'You entered {position} instead of a positive integer. Please try again.')

    @is_channel(channel_ids)
    @commands.command()
    async def rlength(self, ctx, _type):
        ''': Check the length of the queue'''
        if self.qtoggle:
            if _type.lower() == 'group':
                if not self.grouped_queue.empty:
                    grouped_length = len(self.grouped_queue)
                    await ctx.author.send(f'The queue for the current pokemon is {grouped_length} members long.')
                else: 
                    await ctx.author.send('The group queue is empty.')
            elif _type.lower() == 'overall':
                if not self.queue.empty:
                    length = len(self.queue)
                    await ctx.author.send(f'The overall queue is {length} members long.')
                else:
                    await ctx.author.send('The overall queue is empty.')
            else:
                await ctx.author.send(f'{_type} is not a valid queue type. Please enter either "overall" or "group" as a queue type.')
        else:
            await ctx.author.send('The queue is closed.')

    @is_channel(channel_ids)
    @commands.command()
    async def rupdate(self, ctx, pokemon):
        ''': Changes the users previous pokemon with a new one.'''
        author = ctx.author
        if self.qtoggle:
            if pokemon.lower() in available_pokemon:
                if not self.queue.empty:
                    for place in np.where(self.queue[self.queue['user_id'] == author.id])[0]:
                        self.queue.iloc[[place],2] = pokemon.lower()
                    await ctx.author.send('Your entry in the queue has been updated.')
                else:
                    await ctx.author.send('The queue is empty.')
            else: 
                await ctx.author.send(f'{pokemon} is an invalid pokemon. Please ensure you enter one of the following pokemon: \n' + ', '.join(available_pokemon))
        else:
            await ctx.author.send('The queue is closed.')        

    @is_approved()
    @commands.command()
    async def rapprove(self, ctx):
        ''': Adds a user to the approved users list.'''
        user = ctx.message.mentions[0]
        if user.id not in self.approved_users:
            self.approved_users.append(user.id)
            await ctx.send(f'{user.mention} has been added to the approved users list.')
        else:
            await ctx.send(f'{user.mention} is already in the approved users list.')

    @is_approved()
    @commands.command()
    async def runapprove(self, ctx):
        ''': Removes a user from the approved users list.'''
        user = ctx.message.mentions[0]
        if user.id in self.approved_users:
            self.approved_users.remove(user.id)
            await ctx.send(f'{user.mention} has been removed from the approved users list.')
        else: 
            await ctx.send(f'{user.mention} is not in the approved users list.')

    @is_approved()
    @commands.command()
    async def rmremove(self, ctx):
        ''': Remove another member from the entire queue'''
        user = ctx.message.mentions[0]
        if user.id not in self.queue['user_id'].tolist() and user.id not in self.grouped_queue['user_id'].tolist():
            await ctx.author.send(f'{user.mention} is not in the queue.')
        else:
            if user.id in self.grouped_queue['user_id'].tolist():
                self.grouped_queue = self.grouped_queue[self.grouped_queue['user_id'] != user.id].reset_index(drop = True)
                self.queue_history = self.queue_history[self.queue_history['user_id'] != user.id].reset_index(drop = True)
                await ctx.author.send(f'{user.mention} has been removed from the group queue.')

            # want to do both above and below statement, hence why no else statement
            if user.id in self.queue['user_id'].tolist():
                self.queue = self.queue[self.queue['user_id'] != user.id].reset_index(drop = True)
                self.queue_history = self.queue_history[self.queue_history['user_id'] != user.id].reset_index(drop = True)
                await ctx.author.send(f'{user.mention} has been removed from the overall queue.')

    @is_approved()
    @commands.command()
    async def rfilter(self, ctx, pokemon):
        ''': Filters the queue by the specified pokemon'''
        if self.grouped_queue.empty:
            if pokemon.lower() in available_pokemon:
                self.grouped_queue = self.queue[self.queue['pokemon'] == pokemon.lower()].reset_index(drop = True)
                self.queue = self.queue[self.queue['pokemon'] != pokemon.lower()].reset_index(drop = True)
                await ctx.author.send(f'The queue has now been filtered to the following pokemon: {pokemon}')
            else:
                await ctx.author.send(f'{pokemon} is an invalid pokemon. Please ensure you enter one of the following pokemon: \n' + ', '.join(available_pokemon))
        else:
            await ctx.author.send('There are still members remaining in the current grouped queue. Please finish/clear the remaining queue before creating a new one.')

    @is_approved()
    @commands.command()
    async def rnext(self, ctx, raid_code):
        ''': Call the next member in the queue'''
        if raid_code.isdigit() and len(raid_code) == 4:
            if not self.grouped_queue.empty:
                if len(self.grouped_queue) > 0:
                    member = discord.utils.get(ctx.guild.members, id=self.grouped_queue.iloc[[0],:]['user_id'][0])
                    await member.send(f"It's your turn to raid! Please make sure you add Alec's FC below.\nIf you cannot make it or you are having issues joining please inform Alec ASAP. If you are a no-show you will be skipped. Good luck and have fun!\n```Code: {raid_code} \nFC: 8119-6654-7598 (thall)```")
                    await ctx.author.send(f"It is now {member.mention}'s turn to raid with the following code: `{raid_code}`")
                    self.grouped_queue = self.grouped_queue.iloc[1:]
                else:
                    await ctx.author.send('Queue is empty.')
            else:
                await ctx.author.send('Please group the queue by pokemon before going to the next entry.')
        else:
            await ctx.author.send(f'Your raid code of `{raid_code}` is invalid. Please try again.')

    @is_approved()
    @commands.command()
    async def rclear(self, ctx, _type):
        ''': Clears a specific queues'''
        if _type.lower() == 'overall':
            self.queue = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])
            await ctx.author.send('Overall queue has been cleared.')
        elif _type.lower() == 'group':
            self.grouped_queue = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])
            await ctx.author.send('Group queue has been cleared.')
        elif _type.lower() == 'both':
            self.grouped_queue = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])
            self.queue = pd.DataFrame(columns = ['user_id', 'username', 'pokemon', 'time'])
            await ctx.author.send('Both queues have been cleared.')
        else:
            await ctx.author.send(f'{_type} is not a valid queue type. Please enter either "overall", "group", or "both" as a queue type.')
        
    @is_approved()
    @commands.command()
    async def rtoggle(self, ctx):
        ''': Toggles the queue'''
        self.qtoggle = not self.qtoggle
        if self.qtoggle:
            state = 'OPEN'
        else:
            state = 'CLOSED'
        await ctx.send(f'Re-roll queue is now {state}.')

    @is_approved()
    @commands.command()
    async def rexport(self, ctx, file_name):
        ''': Exports the current queue to a .csv file'''
        usernames = [ctx.guild.get_member(i) for i in self.queue_history['user_id'].tolist()]
        file_path = Path(f'queue_logs/{file_name}.csv')
        df = pd.DataFrame({'user_id': self.queue_history['user_id'].tolist(), 'user': usernames, 'pokemon': self.queue_history['pokemon'].tolist(), 'time': self.queue_history['time'].tolist()})
        df.to_csv(file_path)
        await ctx.author.send(f'A .csv file has been saved to {file_path}.')

bot.add_cog(Queue(bot))
bot.add_cog(rQueue(bot))

bot.run(token)