import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from columns_creation_funcs import construct_emoji
from models import *

class PublicCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @app_commands.command(name="create-player",description="Creates a player for the user")
    async def create_player(self,interaction: discord.Interaction):
        new_player = User(user_id=str(interaction.user.id),user_name=str(interaction.user.name))
        session.add(new_player)
        session.commit()

        player_created_embed = discord.Embed(title="Created a new player",description=f"New player for {new_player.user_name} has successfully been made.")
        await interaction.response.send_message(embed=player_created_embed)
    @app_commands.command(name="set-image",description="Sets the profile image for the player")
    async def set_image(self,interaction: discord.Interaction):
        user_data = session.query(User).filter_by(user_id=str(interaction.user.id)).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        await interaction.response.send_message("Send the image now")
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel and msg.attachments
        try:
            msg = await self.bot.wait_for("message",timeout=20,check=check)
            profile_image = msg.attachments[0]
            print(profile_image,type(profile_image))
            user_data.image_url = str(profile_image)
            session.commit()
            await interaction.followup.send(f"Your image was stored. {profile_image.url}")
        except asyncio.TimeoutError:
            await interaction.followup.send("It took you too long to send the image")
    @app_commands.command(name="remove-image",description="Removes the profile image for the player")
    async def remove_image(self,interaction:discord.Interaction):
        user_data = session.query(User).filter_by(user_id=str(interaction.user.id)).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        user_data.image_url = None
        session.commit()
        await interaction.response.send_message("Successfully removed users profile image.")

    @app_commands.command(name="my-party",description="Sends some data of the users player")
    async def my_party(self,interaction: discord.Interaction):
        user_data = session.query(User).filter_by(user_id=str(interaction.user.id)).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        guild = interaction.guild
        user = await guild.fetch_member(int(user_data.user_id))
        user_server_name = user.display_name
        if user_server_name:
            print(user_server_name)
        else:
            print("Failed to retrieve user_server")

        first_pokemon_data = session.query(Pokemon).filter_by(id=str(user_data.first_pokemon_id)).first()
        second_pokemon_data = session.query(Pokemon).filter_by(id=str(user_data.second_pokemon_id)).first()
        third_pokemon_data = session.query(Pokemon).filter_by(id=str(user_data.third_pokemon_id)).first()

        users_player_embed = discord.Embed(title=f"{user_server_name}'s data", color=discord.Color.blue())
        users_player_embed.set_thumbnail(url=user_data.image_url)
        users_player_embed.add_field(name="Name", value=user_server_name)

        if first_pokemon_data:
            emoji = session.query(Emoji).filter_by(id=str(first_pokemon_data.emoji_id)).first()
            emoji = construct_emoji(emoji_name=emoji.name, emoji_id=emoji.emoji_id, animated=emoji.animated,
                                    unicode=emoji.unicode)
            attacks = f"{first_pokemon_data.attack1}\n{first_pokemon_data.attack2}\n{first_pokemon_data.attack3}\n{first_pokemon_data.attack4}"
            first_pokemon_name = f"{emoji}{first_pokemon_data.nickname}"
            first_pokemon_message = f"{attacks}\nNotes: {first_pokemon_data.description}"
            users_player_embed.add_field(name=first_pokemon_name, value=first_pokemon_message, inline=False)
        if second_pokemon_data:
            emoji = session.query(Emoji).filter_by(id=str(second_pokemon_data.emoji_id)).first()
            emoji = construct_emoji(emoji_name=emoji.name, emoji_id=emoji.emoji_id, animated=emoji.animated,
                                    unicode=emoji.unicode)
            attacks = f"{second_pokemon_data.attack1}\n{second_pokemon_data.attack2}\n{second_pokemon_data.attack3}\n{second_pokemon_data.attack4}"
            second_pokemon_name = f"{emoji}{second_pokemon_data.nickname}"
            second_pokemon_message = f"{attacks}\nNotes: {second_pokemon_data.description}"
            users_player_embed.add_field(name=second_pokemon_name, value=second_pokemon_message, inline=False)

        if third_pokemon_data:
            emoji = session.query(Emoji).filter_by(id=str(third_pokemon_data.emoji_id)).first()
            emoji = construct_emoji(emoji_name=emoji.name, emoji_id=emoji.emoji_id, animated=emoji.animated,
                                    unicode=emoji.unicode)
            attacks = f"{third_pokemon_data.attack1}\n{third_pokemon_data.attack2}\n{third_pokemon_data.attack3}\n{third_pokemon_data.attack4}"
            third_pokemon_name = f"{emoji}{third_pokemon_data.nickname}"
            third_pokemon_message = f"{attacks}\nNotes:{third_pokemon_data.description}"
            users_player_embed.add_field(name=third_pokemon_name, value=third_pokemon_message, inline=False)



        await interaction.response.send_message(embed=users_player_embed)

    @app_commands.command(name="help")
    async def help(self,interaction: discord.Interaction):
        help_embed = discord.Embed(title="Help",description="Shows all the commands and what they do.")
        help_embed.add_field(name="create-player",value="Creates a player for the user",inline=False)
        help_embed.add_field(name="my-party",value="Sends some data of the users party",inline=False)
        help_embed.add_field(name="set-image", value="Sets the profile image for the player", inline=False)
        help_embed.add_field(name="remove-image",value="Removes the profile image for the player",inline=False)


        await interaction.response.send_message(embed=help_embed)


async def setup(bot):
    await bot.add_cog(PublicCommands(bot))