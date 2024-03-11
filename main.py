import nextcord
from nextcord.ext import commands
import os
from media_check import *

#Discord Bot
bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="ping command")
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!")

@bot.slash_command(description="check media file data")
async def check(interaction: nextcord.Interaction, media_link: str):
    try:
        file_path=await download_video(media_link, interaction.user.id)
    except Exception as e:
        await interaction.send(e)
        return
    
    try:
        returned_data = await check_video(file_path)
    except Exception as e:
        await interaction.send(e)
        return

    embed=nextcord.Embed(title=f"{returned_data["file_name"]} - Data", color=0x00ff00)
    embed.add_field(name="File Size", value=returned_data["file_size"], inline=False)
    embed.add_field(name="File Type", value=returned_data["file_type"], inline=False)
    embed.add_field(name="File Resolution", value=returned_data["file_resolution"], inline=False)
    embed.add_field(name="File Framecount", value=returned_data["file_framecount"], inline=False)
    embed.add_field(name="File Framerate", value=returned_data["file_framerate"], inline=False)
    embed.add_field(name="File Codec", value=returned_data["file_codec"], inline=False)

    await interaction.send(embed=embed, ephemeral=False)

bot.run(os.getenv("TOKEN"))