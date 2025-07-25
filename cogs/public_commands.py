import discord.app_commands
from discord.ext import commands
class PublicCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @discord.app_commands.command(name="test")
    async def test(self,interaction: discord.Interaction):
        await interaction.response.send_message("The cogs are working")
    discord.app_commands.command(name="help")
    async def help(self,interaction:discord.Interaction):
        help_embed = discord.Embed(title="Help",description="Shows all the commands and what they do.")


async def setup(bot):
    await bot.add_cog(PublicCommands(bot))