import nextcord
from nextcord.ext import commands
import os
from media_check import *

# discord Bot
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="ping command")
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!")

@bot.slash_command(description="check media file data")
async def check(interaction: nextcord.Interaction, attached_file:nextcord.Attachment):
    # download the video
    try:
        
        file_path=await download_video(attached_file)
    
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return await interaction.send("Error downloading video", ephemeral=True)
    
    # analyze video
    try:
        returned_data = await check_video(file_path)
        
        # output
        embed=nextcord.Embed(title=f"{attached_file.filename}", color=0x00ff00)
        embed.add_field(name="Size (MB)", value=returned_data["file_size"], inline=False)
        embed.add_field(name="Type", value=returned_data["file_type"], inline=False)
        embed.add_field(name="Resolution", value=returned_data["file_resolution"], inline=False)
        embed.add_field(name="Frame Count", value=returned_data["file_framecount"], inline=False)
        embed.add_field(name="Frame Rate", value=returned_data["file_framerate"], inline=False)
        embed.add_field(name="Codec", value=returned_data["file_codec"], inline=False)
        embed.set_image(url=attached_file.url)
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.send(embed=embed, ephemeral=False)
    
    except Exception as e:
        print(f"Couldn't analyze video: {str(e)}")
        return await interaction.send("Couldn't analyze video.", ephemeral=True)

bot.run(os.getenv("TOKEN"))