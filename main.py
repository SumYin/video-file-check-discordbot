import nextcord
from nextcord.ext import commands
import os
from video_check import *
from dotenv import load_dotenv

load_dotenv()

# discord Bot
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# ping
@bot.slash_command(description="ping command")
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!")

# info
@bot.slash_command(description="info command")
async def info(interaction: nextcord.Interaction):
    await interaction.send("Bot Source Code: https://github.com/SumYin/video-file-check-discordbot")

# attachment command
@bot.slash_command(description="check attached file data")
async def check_file(interaction: nextcord.Interaction, attached_file:nextcord.Attachment):
    try:
        await interaction.response.defer(ephemeral=True )
        file_path=await download_attachment(attached_file)
        await produce_embed(file_path, interaction)
    
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return await interaction.followup.send("Couldn't download video.", ephemeral=True)
    
# link commmand
@bot.slash_command(description="check link file data")
async def check_link(interaction: nextcord.Interaction, file_link: str):
    try:
        await interaction.response.defer(ephemeral=True )
        file_path=await download_link(file_link, interaction.user.id)
        await produce_embed(file_path, interaction)

    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return await interaction.followup.send("Couldn't download video.", ephemeral=True)

# analyze file and output data
async def produce_embed(file_path, interaction):
    try:
        returned_data = await check_video(file_path)
        
        embed=nextcord.Embed(title=returned_data["file_name"], color=0x00ff00)
        embed.add_field(name="Size (MB)", value=returned_data["file_size"], inline=False)
        embed.add_field(name="Type", value=returned_data["file_type"], inline=False)
        embed.add_field(name="Resolution", value=returned_data["file_resolution"], inline=False)
        embed.add_field(name="Frame Count", value=returned_data["file_framecount"], inline=False)
        embed.add_field(name="Frame Rate", value=returned_data["file_framerate"], inline=False)
        embed.add_field(name="Codec", value=returned_data["file_codec"], inline=False)
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=False)

        os.remove(file_path)
    
    except Exception as e:
        print(f"Error producing embed: {str(e)}")
        os.remove(file_path)
        return await interaction.followup.send("Couldn't analyze video.", ephemeral=True)

bot.run(os.getenv("TOKEN"))