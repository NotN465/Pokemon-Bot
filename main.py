import json

import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,relationship
from sqlalchemy import Column, Integer, String,ForeignKey
# boilerplate code

engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

with open("token.txt","r") as f:
    token = f.read()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.',intents=intents)

# on ready event
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user}, ID: {bot.user.id} is ready.")
@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"Joined {guild.name}, trying to create the create/edit role")
    try:
        with open("config.json") as f:
            data = json.load(f)
        role = await guild.create_role(name=data["pokemon_handler_role"],
                                       permissions=discord.Permissions(),
                                       reason="This role is used just for creating/editing users pokemons")
    except discord.Forbidden:
        print("Bot doesnt have the permission to create this role")
    except Exception as e:
        print(f"Error: {e}")


async def main():
    async with bot:
        await bot.load_extension("cogs.public_commands")
        await bot.load_extension("cogs.admin_commands")
        await bot.start(token)
asyncio.run(main())


