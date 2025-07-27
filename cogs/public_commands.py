import discord
from discord import app_commands
from discord.ext import commands
from models import *

class PublicCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @app_commands.command(name="create-player",description="creates a new player")
    async def create_player(self,interaction:discord.Interaction):
        new_player = User(user_id=str(interaction.user.id),user_name=str(interaction.user.name))
        session.add(new_player)
        session.commit()

        player_created_embed = discord.Embed(title="Created a new player",description=f"New player for {new_player.user_name} has successfully been made.")
        await interaction.response.send_message(embed=player_created_embed)

    @app_commands.command(name="help")
    async def help(self,interaction:discord.Interaction):
        help_embed = discord.Embed(title="Help",description="Shows all the commands and what they do.")


async def setup(bot):
    await bot.add_cog(PublicCommands(bot))