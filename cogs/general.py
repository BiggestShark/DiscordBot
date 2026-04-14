import discord
from discord.ext import commands

class General( commands.Cog ):
    def __init__( self , bot ):
        self.bot = bot
        
    #模組內的指令需使用@commands.commands()
    @commands.command()
    async def ping( self , ctx ):
        await ctx.send( 'Pong!' )
        
#定義setup函式，供main.py載入此模組
async def setup( bot ):
    await bot.add_cog( General( bot ) )