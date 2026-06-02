import discord
from discord.ext import commands
from discord import app_commands
import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

class VoiceLogs( commands.Cog ):
    def __init__( self , bot ):
        self.bot = bot
        
        #格式: { channel_id: [ ( timestamp , user , action ) , ... ] }
        self.logs = {}
        
    def _add_log( self , channel_id , timestamp , user , action ):
        if channel_id not in self.logs:
            self.logs[channel_id] = []
        self.logs[channel_id].append( ( timestamp , user , action ) )
        
        #只保留最後30筆
        self.logs[channel_id] = self.logs[channel_id][-20:]
        
    @commands.Cog.listener()
    async def on_voice_state_update( self , member , before , after ):
        #若頻道沒有變化，則忽略
        if before.channel == after.channel:
            return

        time_str = datetime.now( ZoneInfo( "Asia/Taipei" ) ).strftime( '%Y/%m/%d %H:%M:%S' )
        
        #記錄進入頻道
        if after.channel:
            self._add_log( after.channel.id , time_str , member.display_name , 'Join' )
            
        #記錄離開頻道
        if before.channel:
            self._add_log( before.channel.id , time_str , member.display_name , 'Leave' )
            
    #使用app_command支援斜線指令
    @app_commands.command( name = "showlog" , description = "顯示特定語音頻道的進出記錄" )
    async def showlog( self , interaction : discord.Interaction , channel : discord.VoiceChannel ):
        records = self.logs.get( channel.id , [] )
        
        message_content = f"**頻道ID `{ channel.name }` 的進出記錄：**\n"
        
        if not records:
            await interaction.response.send_message( f"`{ channel.name }`無記錄" )
            return
        
        #延遲回應避免斜線指令超時
        await interaction.response.defer()
        
        for timestamp , user , action in records:
            action_tw = "進入" if action == 'Join' else "離開"
            line = f"`[{ timestamp }]` 👤 **[{ user }]** { action_tw }\n"
            
            #檢查是否即將超過DC 2000字元限制 (保留緩衝)
            if len( message_content ) + len( line ) > 1900:
                await interaction.response.send_message( message_content )
                
                #先清空
                message_content = ""
                
            message_content += line
            
        if message_content:
            await interaction.followup.send( message_content )
            
async def setup( bot ):
    await bot.add_cog( VoiceLogs( bot ) )