import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import glob

class YTDLBOT( commands.Cog ): 
    def __init__( self , bot ):
        self.bot = bot
        
    @app_commands.command( name = "download" , description = "下載YT影片或音訊" )
    @app_commands.describe(
        url = "影片網址",
        media_type = "選擇影片或音訊",
        audio_quality = "選擇音質( 預設192k )",
        volume = "音量大小",
        start_time = "開始時間( 選填，格式為 hh : mm : ss )",
        end_time = "結束時間( 選填，格式為 hh : mm : ss )"
    )
    @app_commands.choices(
        media_type = [
            app_commands.Choice( name = "影片( mp4 )" , value = "video" ),
            app_commands.Choice( name = "音訊( mp3 )" , value = "audio" )
        ],
        audio_quality = [
            app_commands.Choice( name = "320k" , value = "320k" ),
            app_commands.Choice( name = "192k" , value = "192k" ),
            app_commands.Choice( name = "128k" , value = "128k" )
        ],
        volume = [
            app_commands.Choice( name = "0.5x" , value = "0.5" ),
            app_commands.Choice( name = "1.0x" , value = "1.0" ),
            app_commands.Choice( name = "0.5x" , value = "1.5" ),
            app_commands.Choice( name = "2.0x" , value = "2.0" )
        ])
    
    async def download_media(
        self,
        interation : discord.Interaction,
        url : str,
        media_type : app_commands.Choice[str],
        audio_quality : app_commands.Choice[str] = None,
        volume : app_commands.Choice[str] = None,
        start_time : str = None,
        end_time : str = None ):
        
        #延遲回覆，避免下載時間超過discord規定的3秒限制
        await interation.response.defer()
        
        #設定輸出檔名為interation ID
        output_template = f"{ interation.id }.%( ext )s"
        cmd = ['yt-dlp' , url , '-o' , output_template]
        
        #音質預設值
        quality_val = audio_quality.value if audio_quality else "192k"
        
        #輸出格式
        if media_type.value == 'audio':
            cmd.extend([
                '-f',
                'bestaudio',
                '--extract-audio',
                '--audio-format',
                'mp3',
                'audio_quality',
                'quality_val'
            ])
        else:
            cmd.extend([
                '-f',
                'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '--merge-output-format',
                'mp4'
                ])
        
        #音量設定
        volume_val = volume.value if volume else "1.0"
        if volume_val != "1.0":
            cmd.extend( ['--postprocessor-args' , f"-filter:a volume={ volume_val }"] )
        
        #時間段
        if start_time or end_time:
            cmd.extend( ['--download-sections' , f'*{ start_time } - { end_time }'] )
            
        try:
            #執行yt-dlp指令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            #尋找下載完成的檔案
            files = glob.glob( f"{ interation.id }.*" )
            if not files:
                await interation.followup.send( f"下載失敗")
                return
            
            file_path = files[0]
            file_size = os.path.getsize( file_path )
            
            #discord預設檔案最大5mb
            if file_size > 5 *1024 * 1024:
                await interation.followup.send( f"下載完成，但是檔案大小( { file_size /1024 / 1024 :.2f } mb )，超過5mb限制")
                
            else:
                #傳送檔案
                await interation.followup.send( file = discord.File( file_path ) )
                
        except Exception as e:
            await interation.followup.send( f"發生錯誤: { e }" )
        finally:
            #清理下載的檔案
            for f in glob.glob( f"{ interation.id }.*" ):
                try:
                    os.remove( f )
                except OSError:
                    pass
                
    async def setup( bot ):
        await bot.add_cog( YTDLBOT( bot ) )