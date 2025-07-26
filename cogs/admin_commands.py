import json
import discord.app_commands
from discord.ext import commands

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Models created specifically for this bot
from columns_creation_funcs import user_already_created,emoji_already_created,user_creation,emoji_creation,pokemon_creation,construct_emoji
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
        if emoji == None:
            await interaction.response.send_message("That emoji doesn't exist in the current server.")
            return
        if not emoji_already_created(str(emoji.id)):
            emoji = emoji_creation(emoji_id=str(emoji.id),name=emoji.name,animated=emoji.animated,guild_id=emoji.guild_id)
        else:
            emoji = session.query(Emoji).filter_by(emoji_id=str(emoji.id)).first()
        new_pokemon = pokemon_creation(nickname=nickname,emoji_id=emoji.emoji_id,
                         attack1=attack1,attack2=attack2,attack3=attack3,attack4=attack4,description=misc)
        creation_embed = discord.Embed(title="Pokemon created",color=discord.Colour.brand_green())
        creation_embed.add_field(name="Nickname ",value=new_pokemon.nickname)

        created_emoji = construct_emoji(emoji_name=emoji.name,emoji_id=emoji.emoji_id,animated=emoji.animated)
        print(created_emoji)
        creation_embed.add_field(name="Emoji", value=created_emoji)

        creation_embed.add_field(name="attack1",value=new_pokemon.attack1,inline=False)
        creation_embed.add_field(name="attack2",value=new_pokemon.attack2,inline=False)
        creation_embed.add_field(name="attack3",value=new_pokemon.attack3,inline=False)
        creation_embed.add_field(name="attack4",value=new_pokemon.attack4,inline=False)

        creation_embed.add_field(name="misc",value=new_pokemon.description,inline=False)

        await interaction.response.send_message(embed=creation_embed)
    @discord.app_commands.command(name="give-pokemon",description="Gives a created pokemon by its name")
    @discord.app_commands.describe(user="User Ping",pokemon_name="Pokemon name")
    async def give_pokemon(self,interaction:discord.Interaction,user: discord.Member,pokemon_name: str):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        user_data = session.query(User).filter_by(user_id=str(user.id)).first()
        # Error handler for the user
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        pokemon_data = session.query(Pokemon).filter_by(nickname=pokemon_name).first()
        # Error handler for the pokemon
        if not pokemon_data:
            await interaction.response.send_message("Pokemon with that name doesn't exist.")
            return
        selected_pokemon_place = None
        pokemon_ids = [user_data.first_pokemon_id,user_data.second_pokemon_id,user_data.third_pokemon_id]
        for i in range(len(pokemon_ids)):
            if not pokemon_ids[i]:
                selected_pokemon_place = i
                break

        # Error handler for pokemons place
        print(selected_pokemon_place)
        if selected_pokemon_place == None:
            await interaction.response.send_message("There is no space for another pokemon for this player.")
            return

        if selected_pokemon_place == 0:
            user_data.first_pokemon_id = pokemon_data.id
        if selected_pokemon_place == 1:
            user_data.second_pokemon_id = pokemon_data.id
        if selected_pokemon_place == 2:
            user_data.third_pokemon_id = pokemon_data.id
        session.commit()
        embed = discord.Embed(title="Added a new pokemon",description=f"Added a new pokemon called {pokemon_data.nickname} to {user_data.user_name}",color=discord.Colour.brand_green())

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="check-user",description="Checks the pokemons of the user and sends them to the command caller")
    @discord.app_commands.describe(user="User Ping")
    async def check_user(self,interaction:discord.Interaction,user:discord.Member):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        user_data = session.query(User).filter_by(user_id=str(user.id)).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return

        first_pokemon_data = session.query(Pokemon).filter_by(id=str(user_data.first_pokemon_id)).first()
        second_pokemon_data = session.query(Pokemon).filter_by(id=str(user_data.second_pokemon_id)).first()
        third_pokemon_data = session.query(Pokemon).filter_by(id=str(user_data.third_pokemon_id)).first()
        first_pokemon_message = "No pokemon"
        second_pokemon_message = "No pokemon"
        third_pokemon_message = "No pokemon"

        if first_pokemon_data:
            emoji = session.query(Emoji).filter_by(emoji_id=str(first_pokemon_data.emoji_id)).first()
            emoji = construct_emoji(emoji_name=emoji.name,emoji_id=emoji.emoji_id,animated=emoji.animated)
            attacks = f"Attack 1: {first_pokemon_data.attack1}\nAttack2: {first_pokemon_data.attack2}\nAttack 3: {first_pokemon_data.attack3}\nAttack 4: {first_pokemon_data.attack4}"
            first_pokemon_message = f"Nickname: {first_pokemon_data.nickname}\nEmoji: {emoji}\n{attacks}\nMisc:{first_pokemon_data.description}"
        if second_pokemon_data:
            emoji = session.query(Emoji).filter_by(emoji_id=str(second_pokemon_data.emoji_id)).first()
            emoji = construct_emoji(emoji_name=emoji.name,emoji_id=emoji.emoji_id,animated=emoji.animated)
            attacks = f"Attack 1: {second_pokemon_data.attack1}\nAttack2: {second_pokemon_data.attack2}\nAttack 3: {second_pokemon_data.attack3}\nAttack 4: {second_pokemon_data.attack4}"
            second_pokemon_message = f"Nickname: {second_pokemon_data.nickname}\nEmoji: {emoji}\n{attacks}\nMisc:{second_pokemon_data.description}"
        if third_pokemon_data:
            emoji = session.query(Emoji).filter_by(emoji_id=str(third_pokemon_data.emoji_id)).first()
            emoji = construct_emoji(emoji_name=emoji.name,emoji_id=emoji.emoji_id,animated=emoji.animated)
            attacks = f"Attack 1: {third_pokemon_data.attack1}\nAttack2: {third_pokemon_data.attack2}\nAttack 3: {third_pokemon_data.attack3}\nAttack 4: {third_pokemon_data.attack4}"
            third_pokemon_message = f"Nickname: {third_pokemon_data.nickname}\nEmoji: {emoji}\n{attacks}\nMisc:{third_pokemon_data.description}"

        check_user_embed = discord.Embed(title=f"{user_data.user_name}'s data",color=discord.Color.blue())
        check_user_embed.set_thumbnail(url=user.avatar.url)
        check_user_embed.add_field(name="Name",value=user_data.user_name)
        check_user_embed.add_field(name="ID",value=user_data.user_id)

        # Pokemon fields
        check_user_embed.add_field(name="First Pokemon",value=first_pokemon_message,inline=False)
        check_user_embed.add_field(name="Second Pokemon",value=second_pokemon_message,inline=False)
        check_user_embed.add_field(name="Third Pokemon",value=third_pokemon_message,inline=False)

        await interaction.response.send_message(embed=check_user_embed,ephemeral=True)
    @discord.app_commands.command(name="take-pokemon")
    @discord.app_commands.describe(user="User Ping",pokemon_option="Pokemon")
    @discord.app_commands.choices(pokemon_option=[
        discord.app_commands.Choice(name="First Pokemon", value='1'),
        discord.app_commands.Choice(name="Second Pokemon", value='2'),
        discord.app_commands.Choice(name="Third Pokemon", value='3')
    ])
    async def take_pokemon(self,interaction:discord.Interaction,user: discord.Member,pokemon_option: discord.app_commands.Choice[str]):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        user_data = session.query(User).filter_by(user_id=user.id).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        # I know there is a better way to do this...
        choice = False
        if pokemon_option.value == '1':
            user_data.first_pokemon_id = None
            choice = True
        elif pokemon_option.value == '2':
            user_data.second_pokemon_id = None
            choice = True
        elif pokemon_option.value == '3':
            user_data.third_pokemon_id = None
            choice = True
        if not choice:
            await interaction.response.send_message("That slot doesn't have a pokemon.")
            return
        session.commit()
        await interaction.response.send_message(f"The pokemon has successfully been taken from {user.name}")
    @d
    @discord.app_commands.command(name="Edit Pokemon",description="Edits a pokemon, empty fields don't cause any change")
    @discord.app_commands.describe(ID="Pokemon ID",Nickname="Nickname",Emoji="Emoji Name",Attack1="First Attack",Attack2="Second Attack",Attack3="Third Attack",Attack4="Forth Attack",Misc="Misc")
    async def edit_pokemon(self,interaction:discord.Interaction,ID: int,Nickname: str,Emoji: str,Attack1: str,Attack2: str,Attack3: str,Attack4: str,Misc: str):
        pass


    @discord.app_commands.command(name="test")
    async def test(self,interaction:discord.Interaction):
        emoji = construct_emoji(emoji_name="ZGeconomy",emoji_id=1397968517328015521,animated=False)
        await interaction.response.send_message(emoji)

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