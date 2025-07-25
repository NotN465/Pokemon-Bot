import json
import discord.app_commands
from discord.ext import commands

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Models created specifically for this bot
from columns_creation_funcs import user_already_created,emoji_already_created,user_creation,emoji_creation,pokemon_creation
from models import Pokemon,User,Emoji

engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

with open(r"D:\pythonProject1\Pokemon bot\config.json") as f:
    data = json.load(f)
class AdminCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.role_name = data["pokemon_handler_role"]


    @discord.app_commands.command(name="create")
    @discord.app_commands.describe(nickname="nickname",emoji="icon",attack1="attack 1",attack2="attack 2",attack3="attack 3",attack4="attack 4",misc="misc")
    async def create(self,interaction: discord.Interaction,nickname: str,emoji: str,attack1: str,attack2: str,attack3: str,attack4: str,misc: str = ""):
        required_role = discord.utils.get(interaction.guild.roles,name=self.role_name)
        if required_role not in interaction.user.roles: # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        emoji = discord.utils.get(interaction.guild.emojis,name=emoji)
        if not emoji_already_created(str(emoji.id)):
            emoji = emoji_creation(emoji_id=str(emoji.id),name=emoji.name,animated=emoji.animated,guild_id=emoji.guild_id)
        else:
            emoji = session.query(Emoji).filter_by(emoji_id=str(emoji.id)).first()
        pokemon_creation()



        await interaction.response.send_message(f"name: {nickname}, attack 1: {attack1}, misc: {misc}, {test_emoji}")

    @discord.app_commands.command(name="admin-help")
    async def admin_help(self,interaction:discord.Interaction):
        required_role = discord.utils.get(interaction.guild.roles,name=self.role_name)
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permissions for this command")
            return
        help_embed = discord.Embed(title="Admin Help",description="Shows all the admin commands and what they do.")
        help_embed.add_field(name="create",value="Used for creating new pokemons, all fields are required except misc.",inline=False)
        await interaction.response.send_message(embed=help_embed,ephemeral=True)
        
#@app_commands.describe(id="ID",title="title",content="content",checkmark="check mark")
#async def edit_a_wish(interaction:discord.Interaction,id: str, title: str = "optional", content: str = "optional", checkmark: bool = False):


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))