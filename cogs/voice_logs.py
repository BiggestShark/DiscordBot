import discord
from discord.ext import commands
import datetime
import csv
import io

class VoiceLogs( commands.Cog ):
    def __init__( self , bot ):
        self.bot = bot
        
        #格式: { channel_id: [ ( timestamp , user , action ) , ... ] }
        self.logs = {}
        
    def _add_log( self , channel_id , timestamp , user , action ):
        if channel_id not in self.logs:
            self.logs[channel_id] = []
        self.logs[channel_id].append( ( timestamp , user , action ) )
        
    @commands.Cog.listener()
    async def on_voice_state_update( self , member , before , after ):
        if before.channel == after.channel:
            return
        
        log_channel = self.bot.get_channel( self.log_channel_id )
        if not log_channel:
            return
        
        time_str = datetime.datetime.now().strftime( '%Y/%m/%d %H:%M:%S' )
        
        #記錄進入頻道
        if after.channel and after.channel_id == self.target_voice_id:
            await log_channel.send( f"`[{ time_str }]` 👤 **{ member.display_name }** 進入了 `{ after.channel.name }`" )
            
        #記錄離開頻道
        if before.channel and before.channel_id == self.target_voice_id:
            await log_channel.send( f"`[{ time_str }]` 👤 **{ member.display_name }** 離開了 `{ after.channel.name }`" )
            
    @commands.command()
    async def showlog( self , ctx , * , channel: discord.VoiceChannel ):
        records = self.logs.get( channel.id , [] )
        
        message_content = f"**頻道ID `{ channel.name }` 的進出記錄：**\n"
        
        if not records:
            await ctx.send( f"`{ channel.name }`無記錄" )
            return
        
        for timestamp , user , action in records:
            action_tw = "進入" if action == 'Join' else "離開"
            line = f"`[{ timestamp }]` 👤 **[{ user }]** { action_tw }\n"
            
            #檢查是否即將超過DC 2000字元限制 (保留緩衝)
            if len( message_content ) + len( line ) > 1900:
                await ctx.send( message_content )
                
                #先清空
                message_content = ""
                
            message_content += line
            
        if message_content:
            await ctx.send( message_content )
        
async def setup( bot ):
    await bot.add_cog( VoiceLogs( bot ) )