import discord
from discord.ext import commands

from pathlib import Path

import pandas as pd
import numpy as np

prefix = '!'  # change this to whatever prefix you'd like
token = 'NjY3MjgwODQ0NzgzNjE2MDAx.XiAcew.KiJz_-KeONfRW782ai09y1rcbUs'

bot = commands.Bot(command_prefix=prefix)

# add roles that can use some commands
approved_roles = ['Administrator', 'Robot', 'Moderator']

def is_approved():
    def predicate(ctx):
        author = ctx.author
        if author is ctx.guild.owner:
            return True
        if any(role.name in approved_roles for role in author.roles):
            return True
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)

@bot.event
async def on_command_error(ctx, error):
    await ctx.author.send(f'Your command resulted in the following error: \n`{error}`')
    
    raise error

class Queue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.qtoggle = False

        # a history of users who have entered the queue
        self.queue_history = [] 

        # add users who have special queue privileges
        self.approved_users = []

    @commands.command()
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
            await ctx.send('The queue is closed.')

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

    @commands.command()
    async def view(self, ctx):
        ''': See who's up next!'''
        guild = ctx.guild
        message = ''
        for place, member_id in enumerate(self.queue):
            member = discord.utils.get(guild.members, id=member_id)
            message += f'**#{place+1}** : {member.mention}\n'
        if message != '':
            await ctx.send(message)
        else:
            await ctx.send('Queue is empty')

    @commands.command()
    async def pos(self, ctx):
        ''': Check your position in the queue'''
        author = ctx.author
        if author.id in self.queue:
            _position = self.queue.index(author.id)+1
            await ctx.author.send(f'You are **#{_position}** in the queue.')
        else:
            await ctx.author.send(f'You are not in the queue, please use {prefix}add to add yourself to the queue.')

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
                await ctx.author.send(f'You are not in the queue, please use {prefix}add to add yourself to the queue.')
        else:
            await ctx.author.send(f'You entered {position} instead of a positive integer. Please try again.')

    @commands.command()
    async def length(self, ctx):
        ''': Check the length of the queue'''
        if self.qtoggle:
            length = len(self.queue)
            await ctx.send(f'The queue is {length} members long.')
        else:
            await ctx.send('The queue is closed.')

    @is_approved()
    @commands.command()
    async def approve(self, ctx):
        ''': Approves a user to give them special queue privileges.'''
        user = ctx.message.mentions[0]
        if user.id not in self.approved_users:
            self.approved_users.append(user.id)
            await ctx.send(f'{user} has been added to the approved users list.')
        else:
            await ctx.send(f'{user} is already in the approved users list.')

    @is_approved()
    @commands.command()
    async def mremove(self, ctx):
        ''': Remove another member from the queue'''
        user = ctx.message.mentions[0]
        if user.id in self.queue:
            self.queue.remove(user.id)
            self.queue_history.remove(user.id)
            await ctx.author.send(f'{user} has been removed from the queue.')
        else:
            await ctx.author.send(f'{user} is not in the queue.')

    @is_approved()
    @commands.command(name='next')
    async def _next(self, ctx, raid_code):
        ''': Call the next member in the queue'''
        if len(self.queue) > 0:
            member = discord.utils.get(ctx.guild.members, id=self.queue[0])
            await member.send(f"It's your turn to raid! Please make sure you add Alec's FC below.\nIf you cannot make it please inform Alec. If you are a no-show you will be skipped. Thanks and enjoy your shiny!\n`Code: {raid_code} \nFC: 8119-6654-7598 (thall)`")
            self.queue.remove(self.queue[0])
        else:
            await ctx.send('Queue is empty.')

    @is_approved()
    @commands.command()
    async def clear(self, ctx):
        ''': Clears the queue'''
        self.queue = []
        await ctx.send('Queue has been cleared.')

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
        user_names = [ctx.guild.get_member(i) for i in self.queue_history]
        file_path = Path(f'queue_logs/{file_name}.csv')
        df = pd.DataFrame({'user': user_names})
        df.to_csv(file_path)
        await ctx.author.send(f'A .csv file has been saved to {file_path}.')

bot.add_cog(Queue(bot))

bot.run(token)