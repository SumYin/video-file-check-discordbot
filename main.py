import os

import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
import cooldowns
from cooldowns import CallableOnCooldown

from dotenv import load_dotenv
from datetime import datetime
import json

from video_check import *

load_dotenv()

# get user data
f = open('user.json')
user = json.load(f)

# discord bot
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_application_command_error(interactions: Interaction, error):
    error = getattr(error, "original", error)
    if isinstance(error, CallableOnCooldown):
        embed=nextcord.Embed(title="Cooldown", description=(f"You are being rate-limited! Retry in `{error.retry_after}` seconds."), color=0xff0000)
        await interactions.send(embed=embed, ephemeral=True)

    elif isinstance(error, PermissionError):
        await interactions.send(
            f"PermissionError"
        )
    else:
        pass

@bot.slash_command(description="test ping")
@cooldowns.cooldown(user["cooldown_times"]["short"][0], user["cooldown_times"]["short"][1], bucket=cooldowns.SlashBucket.author)
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!", ephemeral=True)

# info command
@bot.slash_command(description="get information about this bot")
async def info(interaction: nextcord.Interaction):
    await interaction.send("Bot Source Code: https://github.com/SumYin/video-file-check-discordbot", ephemeral=True)

# rules command
@bot.slash_command(description="check rules")
async def rules(interaction: nextcord.Interaction):
    embed=nextcord.Embed(title=":scroll: __Rules__ | __read carefully__ :scroll:", color=0x000000, description="")
    for rule in user.get("rules"):
        embed.description += rule + "\n"
    await interaction.send(embed=embed, ephemeral=True)

# faq command
@bot.slash_command(description="check frequently asked questions")
async def faq(interaction: nextcord.Interaction):
    embed=nextcord.Embed(title=":grey_question: __Frequently Asked Questions__ :grey_question:", color=0x00000)
    for faq in user.get("faq"):
        embed.add_field(name=faq.get("Q"), value=faq.get("A"), inline=False)
    await interaction.send(embed=embed, ephemeral=True)

# attachment command
@bot.slash_command(description="check attached file data")
@cooldowns.cooldown(user["cooldown_times"]["long"][0], user["cooldown_times"]["long"][1], bucket=cooldowns.SlashBucket.author)
async def check_file(interaction: nextcord.Interaction, attached_file:nextcord.Attachment):
    await interaction.response.defer(ephemeral=True) # we need to decide if ephemeral when we defer, we can't affect this later
    file_path=await download_attachment(attached_file)
    await produce_embed(file_path, interaction, attached_file.filename)
    
# link commmand
@bot.slash_command(description="check link file data")
@cooldowns.cooldown(user["cooldown_times"]["long"][0], user["cooldown_times"]["long"][1], bucket=cooldowns.SlashBucket.author)
async def check_link(interaction: nextcord.Interaction, file_link: str):
    await interaction.response.defer(ephemeral=True) # we need to decide if ephemeral when we defer, we can't affect this later
    file_path=await download_link(file_link, interaction.user.id)
    await produce_embed(file_path, interaction, file_link.split("/")[-1])

# analyze file and output data
async def produce_embed(file_path, interaction, file_name):
    try:
        returned_data = await check_video(file_path)
        
        embed=nextcord.Embed(title=file_name, color=0x000000, timestamp=datetime.now())

        valid = " :white_check_mark:"
        invalid = " :x:"
        check = ""

        # size
        check = invalid
        for prop in user.get("targets").get("size"):
            if returned_data["file_size"] < prop: check = valid
        embed.add_field(name="Size (MB)", value=str(returned_data["file_size"]) + check, inline=False)

        # type
        check = invalid
        for prop in user.get("targets").get("type"):
            if returned_data["file_type"] == prop: check = valid
        embed.add_field(name="Type", value=str(returned_data["file_type"]) + check, inline=False)

        # resolution
        check = invalid
        for prop in user.get("targets").get("resolution"):
            if returned_data["file_resolution"] == prop: check = valid
        embed.add_field(name="Resolution", value=str(returned_data["file_resolution"]) + check, inline=False)

        # frame count
        check = invalid
        for prop in user.get("targets").get("framecount"):
            if returned_data["file_framecount"] == prop: check = valid
        embed.add_field(name="Frame Count", value=str(returned_data["file_framecount"]) + check, inline=False)

        # frame rate
        check = invalid
        for prop in user.get("targets").get("framerate"):
            if returned_data["file_framerate"] == prop: check = valid
        embed.add_field(name="Frame Rate", value=str(returned_data["file_framerate"]) + check, inline=False)

        # codec
        check = invalid
        for prop in user.get("targets").get("codec"):
            if returned_data["file_codec"] == prop: check = valid
        embed.add_field(name="Codec", value=str(returned_data["file_codec"]) + check, inline=False)

        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.followup.send(embed=embed)

        os.remove(file_path)
    
    except Exception as e: # can potentially happen if missing one of the fields above
        print(f"Error producing embed: {str(e)}")
        os.remove(file_path)
        return await interaction.followup.send("Couldn't analyze video.", ephemeral=True)

bot.run(os.getenv("TOKEN"))