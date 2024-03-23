import os

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

import cooldowns
from cooldowns import CallableOnCooldown

from dotenv import load_dotenv
from datetime import datetime
import json

from video_check import *

load_dotenv()

# get host data
f = open('host.json', 'r', encoding='utf-8')
host = json.load(f)
cooldown_short_tokens = host.get("cooldown_times").get("short").get("tokens", 1)
cooldown_short_period = host.get("cooldown_times").get("short").get("period", 5)
cooldown_long_tokens = host.get("cooldown_times").get("long").get("tokens", 1)
cooldown_long_period = host.get("cooldown_times").get("long").get("period", 20)

# discord bot
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}.')
    await bot.change_presence(activity=nextcord.CustomActivity(name="Not official, Community made"))

@bot.event
async def on_application_command_error(interaction: nextcord.Interaction, error: Exception):
    error = getattr(error, "original", error)
    
    # cooldown error
    if isinstance(error, CallableOnCooldown):
        return await produce_error(interaction, "Cooldown", f"You are being rate-limited! Retry in `{error.retry_after}` seconds.", deferred=False)
    
    # permissions error
    elif isinstance(error, PermissionError):
        return await produce_error(interaction, "Command Error", "Permissions error.", deferred=False)

# ping command
@bot.slash_command(description="test ping")
@cooldowns.cooldown(cooldown_short_tokens, cooldown_short_period, bucket=cooldowns.SlashBucket.author)
async def ping(interaction: nextcord.Interaction):
    await interaction.send("pong!", ephemeral=True)

# info command
@bot.slash_command(description="get information about this bot")
@cooldowns.cooldown(cooldown_short_tokens, cooldown_short_period, bucket=cooldowns.SlashBucket.author)
async def info(interaction: nextcord.Interaction):
    await interaction.send("Bot Source Code: https://github.com/SumYin/video-file-check-discordbot", ephemeral=True)

# rules command
@bot.slash_command(description="check rules")
@cooldowns.cooldown(cooldown_short_tokens, cooldown_short_period, bucket=cooldowns.SlashBucket.author)
async def rules(interaction: nextcord.Interaction, language: str = SlashOption(required=False, name="language",choices=host.get("rules").keys(),description="language of the rules")):
    if language==None:
        r = host.get("rules").get(next(iter(host.get("rules"))))
    else:
        r = host.get("rules").get(language)

    embed = nextcord.Embed(title=r.get("title"), color=0x000000, description="")
    for rule in r.get("rules"):
        embed.description += rule + "\n"
    await interaction.send(embed=embed, ephemeral=True)

# faq command
@bot.slash_command(description="check frequently asked questions")
@cooldowns.cooldown(cooldown_short_tokens, cooldown_short_period, bucket=cooldowns.SlashBucket.author)
async def faq(interaction: nextcord.Interaction, language: str = SlashOption(required=False, name="language",choices=host.get("rules").keys(),description="language of the rules")):
    if language==None:
        r = host.get("faq").get(next(iter(host.get("faq"))))
    else:
        r = host.get("faq").get(language)
    
    embed = nextcord.Embed(title=host.get("faq_title"), color=0x00000)
    for faq in r.get("faq"):
        embed.add_field(name=faq.get("Q"), value=faq.get("A"), inline=False)
    await interaction.send(embed=embed, ephemeral=True)

# attachment command
@bot.slash_command(description="check attached file data")
@cooldowns.cooldown(cooldown_long_tokens, cooldown_long_period, bucket=cooldowns.SlashBucket.author)
async def check_file(interaction: nextcord.Interaction, attached_file:nextcord.Attachment):
    await interaction.response.defer(ephemeral=True) # we need to decide if ephemeral when we defer, we can't affect this later
    
    try: file_path = await download_attachment(attached_file)
    except Exception as e: return await produce_error(interaction, "Couldn't Download Video", str(e))
    
    await produce_embed(file_path, interaction, attached_file.filename)

# link commmand
@bot.slash_command(description="check link file data")
@cooldowns.cooldown(cooldown_long_tokens, cooldown_long_period, bucket=cooldowns.SlashBucket.author)
async def check_link(interaction: nextcord.Interaction, file_link: str):
    await interaction.response.defer(ephemeral=True) # we need to decide if ephemeral when we defer, we can't affect this later
   
    try: file_path = await download_link(file_link, interaction.user.id)
    except Exception as e: return await produce_error(interaction, "Couldn't Download Video", str(e))

    await produce_embed(file_path, interaction, file_link.split("/")[-1])

# analyze file, validate properties, and output
async def produce_embed(file_path, interaction, file_name):
    try:
        video_data = await check_video(file_path)
        
        embed = nextcord.Embed(title=file_name, color=0x000000, timestamp=datetime.now())

        valid = " :white_check_mark:"
        invalid = " :x:"

        # size
        check = invalid
        for prop in host.get("targets").get("size"):
            if video_data["file_size"] < prop: check = valid
        embed.add_field(name="Size (MB)", value=str(video_data["file_size"]) + check, inline=False)

        # type
        check = invalid
        for prop in host.get("targets").get("type"):
            if video_data["file_type"] == prop: check = valid
        embed.add_field(name="Type", value=str(video_data["file_type"]) + check, inline=False)

        # resolution
        check = invalid
        for prop in host.get("targets").get("resolution"):
            if video_data["file_resolution"] == prop: check = valid
        embed.add_field(name="Resolution", value=str(video_data["file_resolution"]) + check, inline=False)

        # frame count
        check = invalid
        for prop in host.get("targets").get("framecount"):
            if video_data["file_framecount"] == prop: check = valid
        embed.add_field(name="Frame Count", value=str(video_data["file_framecount"]) + check, inline=False)

        # frame rate
        check = invalid
        for prop in host.get("targets").get("framerate"):
            if video_data["file_framerate"] == prop: check = valid
        embed.add_field(name="Frame Rate", value=str(video_data["file_framerate"]) + check, inline=False)

        # codec
        check = invalid
        for prop in host.get("targets").get("codec"):
            if video_data["file_codec"] == prop: check = valid
        embed.add_field(name="Codec", value=str(video_data["file_codec"]) + check, inline=False)

        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.followup.send(embed=embed)

        os.remove(file_path)
    
    except Exception as e: # can potentially happen if missing one of the fields above
        os.remove(file_path)
        return await produce_error(interaction, "Couldn't Analyze Video", str(e))

async def produce_error(interaction, title, description, debugTitle="", debugDescription="", deferred=True):
    if debugTitle == "": debugTitle = title
    if debugDescription == "": debugDescription = description
    print(f"Error! {debugTitle}: {debugDescription}")

    embed = nextcord.Embed(title=title, color=0xff0000, description=description)
    if deferred: return await interaction.followup.send(embed=embed)
    else: return await interaction.send(embed=embed)

bot.run(os.getenv("TOKEN"))