import discord
from discord.ext import commands
import youtube_dl
import urllib.request
import re
import time

class music(commands.Cog):
    music = {}

    def __init__(self, client):
        self.client = client

    # HELP COMMAND
    # @commands.command()
    # async def help(self, ctx):
    #     await ctx.send('''Here are all of the commands: \n
    #                    !join\tMakes the bot join your VC\n
    #                    !play [song name]\tMakes the bot play your desired song. It will also join the VC if it hasn't already.\n
    #                    !disconnect\tMakes the bot disconnect from the VC you are in.\n
    #                    !createplaylist [playlist name]\tCreates a playlist wih your desired name. Note: you cannot create multiple playlists of the same name and playlists cannot contain a space\n
    #                    !addtoplaylist [playlist name] [song name]\tAdds a song to your playlist.\n
    #                    !removesong [playlist name] [song name]\tRemoves a song from your playlist. Note: if you have the same song multiple times in your playlist, the bot will delete the first instance of the song.\n
    #                    !showplaylist [playlist name]\tDisplays all of the songs within your playlist and the order they will play in.\n
    #                    !playplaylist [playlist name]\tPlays all the songs within your playlist. Currently, the bot will only show it in the order, but we are working on a way so that you can reorder the songs.\n
    #                    !pause\tMakes the bot pause whatever song you are listening to.\n
    #                    !resume\tMakes the bot resume whatever song you are listening to.\n
    #                    !help\tDisplays all possible commands for the bot.\n
    #                    ''')
    
    # JOIN COMMAND
    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            await ctx.send('You aren\'t in a voice channel')
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)


    # DISCONNECT COMMAND
    @commands.command()
    async def disconnect(self,ctx):
        print('here1')
        await ctx.voice_client.disconnect()

    # PLAY COMMAND   
    @commands.command()
    async def play(self,ctx,*query):
        await self.join(ctx)
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        vc = ctx.voice_client
        query_string = ''
        for q in query:
            query_string += q + "+"
        print(query_string)
        if len(query_string) > 0:
            query_string = query_string[:-1]
        html = urllib.request.urlopen('https://www.youtube.com/results?search_query='+query_string)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v="+video_ids[0]
        print(url)
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
            await ctx.send('Playing '+url)
            vc.play(source)

            
    # @commands.command()
    # async def addtoplaylist(self, ctx, playlist, *songs):
    #     if playlist in music:
    #         music[playlist] = music[playlist].extend(songs)

    # CREATE PLAYLISTS       
    @commands.command()
    async def createplaylist(self, ctx, playlist):
        if playlist in music:
            await ctx.send('Playlist called '+str(playlist)+' exists')
            return
        if ' ' in playlist:
            await ctx.send('A space cannot be in your playlist name')
            return
        music[playlist] = []

    # ADD SONG TO PLAYLIST   
    @commands.command()
    async def addtoplaylist(self, ctx, playlist, *song):
        if playlist not in music:
            await ctx.send('Playlist doesn\'t exist')
            return
        song_string = ''
        for s in song:
            song_string += s + ' '
        music[playlist].append(song_string)
        await ctx.send(str(song_string)+' has been added to the playlist '+str(playlist))

    # DELETE SONG FROM PLAYLIST
    @commands.command()
    async def deletesong(self, ctx, playlist, *song):
        if playlist not in music:
            await ctx.send('Playlist doesn\'t exist')
            return
        if song not in music[playlist]:
            await ctx.send('The song '+str(song)+' is not in the playlist '+str(playlist))
        song_string = ''
        for s in song:
            song_string += s + ' '
        await ctx.send(str(song_string)+' has been removed from the playlist '+str(playlist))
    # PRINT PLAYLIST TO USER    
    @commands.command()
    async def showplaylist(self, ctx, playlist):
        if playlist not in music:
            await ctx.send('Playlist doesn\'t exist')
            return
        for i in range(len(music[playlist])):
            await ctx.send('Song #'+str(i+1)+':\t'+str(music[playlist][i]))

    # PLAY THE PLAYLIST        
    @commands.command()
    async def playplaylist(self, ctx, playlist):
        if playlist not in music:
            await ctx.send('Playlist doesn\'t exist')
            return
        for i in range(len(music[playlist])):
            while ctx.voice.client.isplaying() and ctx.voice.client.ispaused():
                time.sleep(500/1000)
            self.play(ctx, music[playlist][i])
        return

    # PAUSE COMMAND
    @commands.command()
    async def pause(self,ctx):
        ctx.voice_client.pause()
        await ctx.send('Paused')

    # RESUME COMMAND
    @commands.command()
    async def resume(self,ctx):
        
        await ctx.voice_client.resume()
        await ctx.send('Resume')

def setup(client):
    client.add_cog(music(client))