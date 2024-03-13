import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

from video_check import *

load_dotenv()

# discord bot
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# ping command
@bot.slash_command(description="ping command")
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!", ephemeral=True)

# info command
@bot.slash_command(description="info command")
async def info(interaction: nextcord.Interaction):
    await interaction.send("Bot Source Code: https://github.com/SumYin/video-file-check-discordbot", ephemeral=True)

# attachment command
@bot.slash_command(description="check attached file data")
async def check_file(interaction: nextcord.Interaction, attached_file:nextcord.Attachment):
    await interaction.response.defer(ephemeral=True)
    file_path=await download_attachment(attached_file)
    await produce_embed(file_path, interaction, attached_file.filename)
    
# link commmand
@bot.slash_command(description="check link file data")
async def check_link(interaction: nextcord.Interaction, file_link: str):
    await interaction.response.defer(ephemeral=True)
    file_path=await download_link(file_link, interaction.user.id)
    await produce_embed(file_path, interaction, file_link.split("/")[-1])

# analyze file and output data
async def produce_embed(file_path, interaction, file_name):
    try:
        returned_data = await check_video(file_path)
        
        embed=nextcord.Embed(title=file_name, color=0x00ff00)
        embed.add_field(name="Size (MB)", value=returned_data["file_size"], inline=False)
        embed.add_field(name="Type", value=returned_data["file_type"], inline=False)
        embed.add_field(name="Resolution", value=returned_data["file_resolution"], inline=False)
        embed.add_field(name="Frame Count", value=returned_data["file_framecount"], inline=False)
        embed.add_field(name="Frame Rate", value=returned_data["file_framerate"], inline=False)
        embed.add_field(name="Codec", value=returned_data["file_codec"], inline=False)
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.followup.send(embed=embed)

        os.remove(file_path)
    
    except Exception as e: # can potentially happen if missing one of the fields above
        print(f"Error producing embed: {str(e)}")
        os.remove(file_path)
        return await interaction.followup.send("Couldn't analyze video.", ephemeral=True)

bot.run(os.getenv("TOKEN"))