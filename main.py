import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

#讀取token
load_dotenv()
TOKEN = os.getenv( 'DISCORD_TOKEN' )

class MyBot( commands.Bot ):
    def __init__( self ):
        #讀取訊息
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        #設定指令前綴!
        super().__init__( command_prefix = '!' , intents = intents )
        
    #覆寫setup_hook函式以在啟動前載入模組
    async def setup_hook(self):
        for filename in os.listdir( './cogs' ):
            if filename.endswith( '.py' ) and filename != '__init__.py':
                #載入模組( 刪除.py副檔名 )
                await self.load_extension( f'cogs.{ filename[ : -3 ] }' )
                print( f'已載入模組: { filename }' )
    
    async def on_ready( self ):
        print( f'已成功登入為{ self.user }' )

#啟動
bot = MyBot()
if __name__ == '__main__':
    bot.run( TOKEN )