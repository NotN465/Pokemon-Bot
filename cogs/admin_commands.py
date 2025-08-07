import json
import discord
from discord import app_commands
from discord.ext import commands


import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Models created specifically for this bot
from columns_creation_funcs import user_already_created,emoji_already_created,user_creation,emoji_creation,pokemon_creation,construct_emoji,is_emoji_custom
from models import Pokemon,User,Emoji

import logging

# logging.basicConfig(level=logging.INFO)
# logging.getLogger("discord").setLevel(logging.DEBUG)

engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

with open(r"D:\pythonProject1\Pokemon bot\config.json") as f:
    data = json.load(f)
class EditPokemon(discord.ui.View):
    def __init__(self,pokemon,bot):
        super().__init__()
        self.bot = bot
        self.pokemon_data = pokemon
        self.create_buttons()
    def attack_callback(self,attack):
        pass


    def create_buttons(self):
        nickname_button = discord.ui.Button(label="Edit Nickname", style=discord.ButtonStyle.green)
        async def nickname_callback(interaction: discord.Interaction):
            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel
            await interaction.response.send_message("Enter the new nickname")
            try:
                msg = await self.bot.wait_for("message", timeout=20, check=check)
                nickname = str(msg.content)
                await interaction.followup.send(f"Successfully renamed the pokemon from {self.pokemon_data.nickname} to {nickname}")
                self.pokemon_data.nickname = nickname
                session.commit()
            except asyncio.TimeoutError:
                await interaction.followup.send("Time for editing has expired.")
        nickname_button.callback = nickname_callback
        emoji_button = discord.ui.Button(label="Edit Emoji", style=discord.ButtonStyle.green)
        async def emoji_callback(interaction: discord.Interaction):
            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel
            await interaction.response.send_message("Enter a new emoji **ONLY THE EMOJI**")
            try:
                msg = await self.bot.wait_for("message",timeout=20,check=check)
                emoji = str(msg.content)
                print("Emoji string:", emoji)
                guild_id = interaction.guild.id

                final_emoji = None
                print("Validating custom emoji")
                custom_emoji_data = is_emoji_custom(emoji)
                print(custom_emoji_data)
                if custom_emoji_data:  # Is the emoji custom
                    emoji_name = custom_emoji_data[0]
                    emoji_id = custom_emoji_data[1]
                    animated = custom_emoji_data[2]
                    if not emoji_already_created(str(emoji_id)):
                        print("Emoji not created yet, creating the emoji...")
                        custom_emoji = emoji_creation(emoji_id=str(emoji_id), name=emoji_name, animated=animated,
                                                      guild_id=guild_id, unicode=False)
                        final_emoji = custom_emoji
                    else:
                        print("Fetching the existing emoji")
                        custom_emoji = session.query(Emoji).filter_by(emoji_id=str(emoji_id)).first()
                    final_emoji = custom_emoji
                else:  # If it isn't a custom emoji, take the normal emoji
                    print("Creating unicode emoji")
                    unicode_emoji = session.query(Emoji).filter_by(name=emoji).first()
                    if not unicode_emoji:
                        unicode_emoji = emoji_creation(emoji_id=None, name=emoji, animated=False, guild_id=None,
                                                       unicode=True)
                    final_emoji = unicode_emoji
                print(final_emoji)

                old_emoji = session.query(Emoji).filter_by(id=self.pokemon_data.emoji_id).first()
                old_emoji_constructed = construct_emoji(old_emoji.name,old_emoji.emoji_id,old_emoji.animated,old_emoji.unicode)
                constructed_emoji = construct_emoji(final_emoji.name,final_emoji.emoji_id,final_emoji.animated,final_emoji.unicode)
                await interaction.followup.send(f"Successfully changed the emoji from {old_emoji_constructed} to {constructed_emoji}")
                self.pokemon_data.emoji_id = final_emoji.id
                session.commit()

            except asyncio.TimeoutError:
                await interaction.followup.send("Time for editing has expired.")
        emoji_button.callback = emoji_callback
        async def attack_callback(interaction:discord.Interaction,attack):
            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel
            await interaction.response.send_message("Enter a new attack")
            try:
                msg = await self.bot.wait_for("message",timeout=20,check=check)
                attack_msg = str(msg.content)
                print(attack_msg)
                if attack == 1:
                    await interaction.followup.send(
                        f"Successfully changed the attack from {self.pokemon_data.attack1} to {attack_msg}")
                    self.pokemon_data.attack1 = attack_msg
                if attack == 2:
                    await interaction.followup.send(
                        f"Successfully changed the attack from {self.pokemon_data.attack2} to {attack_msg}")
                    self.pokemon_data.attack2 = attack_msg
                if attack == 3:
                    await interaction.followup.send(
                        f"Successfully changed the attack from {self.pokemon_data.attack3} to {attack_msg}")
                    self.pokemon_data.attack3 = attack_msg
                if attack == 4:
                    await interaction.followup.send(
                        f"Successfully changed the attack from {self.pokemon_data.attack4} to {attack_msg}")
                    self.pokemon_data.attack4 = attack_msg
                session.commit()
            except asyncio.TimeoutError:
                await interaction.followup.send("Time for editing has expired.")

        async def callback(interaction:discord.Interaction):
            await attack_callback(interaction,1)
        attack1_button = discord.ui.Button(label="Edit Attack 1", style=discord.ButtonStyle.green)
        attack1_button.callback = callback

        async def callback(interaction:discord.Interaction):
            await attack_callback(interaction,2)
        attack2_button = discord.ui.Button(label="Edit Attack 2", style=discord.ButtonStyle.green)
        attack2_button.callback = callback

        async def callback(interaction:discord.Interaction):
            await attack_callback(interaction,3)
        attack3_button = discord.ui.Button(label="Edit Attack 3", style=discord.ButtonStyle.green)
        attack3_button.callback = callback

        async def callback(interaction:discord.Interaction):
            await attack_callback(interaction,4)
        attack4_button = discord.ui.Button(label="Edit Attack 4", style=discord.ButtonStyle.green)
        attack4_button.callback = callback

        async def notes_callback(interaction: discord.Interaction):
            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel
            await interaction.response.send_message("Enter new notes")
            try:
                msg = await self.bot.wait_for("message",timeout=20,check=check)
                notes = str(msg.content)
                await interaction.followup.send(f"Successfully changed notes from {self.pokemon_data.description} to {notes}.")
                self.pokemon_data.description = notes
                session.commit()
            except TimeoutError:
                await interaction.followup.send("Time for editing has expired.")

        notes_button = discord.ui.Button(label="Edit Notes", style=discord.ButtonStyle.green)
        notes_button.callback = notes_callback
        self.add_item(nickname_button)
        self.add_item(emoji_button)
        self.add_item(attack1_button)
        self.add_item(attack2_button)
        self.add_item(attack3_button)
        self.add_item(attack4_button)
        self.add_item(notes_button)



class PageView(discord.ui.View):
    def __init__(self,pokemons,give_buttons,edit_buttons,bot):
        super().__init__()
        self.page = 5
        self.right_button = None
        self.left_button = None
        self.give_buttons = give_buttons
        self.edit_buttons = edit_buttons
        self.give_buttons_list = []
        self.edit_buttons_list = []
        self.bot = bot

        self.left_arrow_button_func()
        self.right_arrow_button_func()
        self.disable_and_enable_buttons(pokemons)
        if give_buttons:
            self.create_give_buttons(pokemons)

        if edit_buttons:
            self.create_edit_buttons(pokemons)


    def right_arrow_button_func(self):
        self.right_button = discord.ui.Button(label="▶️", style=discord.ButtonStyle.blurple)
        async def callback(interaction: discord.Interaction):
            self.page += 5
            pokemons = session.query(Pokemon).all()

            await self.update(interaction,pokemons)
        self.right_button.callback = callback
        self.add_item(self.right_button)

    def left_arrow_button_func(self):
        self.left_button = discord.ui.Button(label="◀️", style=discord.ButtonStyle.blurple)
        async def callback(interaction: discord.Interaction):
            self.page -= 5
            pokemons = session.query(Pokemon).all()

            await self.update(interaction, pokemons)
        self.left_button.callback = callback
        self.add_item(self.left_button)
    def make_give_callback(self,pokemon,pokemons):
        async def callback(interaction: discord.Interaction):
            user_data = session.query(User).filter_by(user_id=str(interaction.user.id)).first()
            if not user_data.first_pokemon_id:
                user_data.first_pokemon_id = pokemon.id
            elif not user_data.second_pokemon_id:
                user_data.second_pokemon_id = pokemon.id
            elif not user_data.third_pokemon_id:
                user_data.third_pokemon_id = pokemon.id
            else:
                await interaction.response.send_message("There is no more pokemon space for that player",
                                                        ephemeral=True)
                return
            session.commit()
            await self.update(interaction, pokemons)

        return callback

    def make_edit_callback(self,pokemon):
        async def callback(interaction: discord.Interaction):
            view = EditPokemon(pokemon,self.bot)
            emoji = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            constructed_emoji = construct_emoji(emoji_id=emoji.emoji_id,emoji_name=emoji.name,animated=emoji.animated,unicode=emoji.unicode)
            self.clear_items()
            await interaction.response.send_message(f"Select what field would you like to edit for {constructed_emoji}{pokemon.nickname}",view=view)

        return callback

    def create_give_buttons(self,pokemons):
        displayed_pokemons = pokemons[self.page-5:self.page]
        emoji = None
        for pokemon in displayed_pokemons:
            emoji_data = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            if emoji_data.unicode:
                emoji = str(emoji_data.name)
            else:
                emoji = discord.PartialEmoji(name=emoji_data.name,id=emoji_data.emoji_id,animated=emoji_data.animated)
            label = f"{pokemon.nickname}"
            button = discord.ui.Button(emoji=emoji,label=label,style=discord.ButtonStyle.green)
            button.callback = self.make_give_callback(pokemon,pokemons)
            self.add_item(button)
            self.give_buttons_list.append(button)

    def create_edit_buttons(self,pokemons):
        displayed_pokemons = pokemons[self.page-5:self.page]
        emoji = None
        for pokemon in displayed_pokemons:
            print(f"Creating a new edit button for {pokemon.nickname}")
            emoji_data = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            if emoji_data.unicode:
                emoji = str(emoji_data.name)
            else:
                emoji = discord.PartialEmoji(name=emoji_data.name,id=emoji_data.emoji_id,animated=emoji_data.animated)
            label = f"{pokemon.nickname}"
            button = discord.ui.Button(emoji=emoji,label=label,style=discord.ButtonStyle.green)
            button.callback = self.make_edit_callback(pokemon)
            self.add_item(button)
            self.edit_buttons_list.append(button)


    def disable_and_enable_buttons(self,pokemons):
        # Logic for disabling/enabling the left button
        if self.page == 5:
            self.left_button.disabled = True
        else:
            self.left_button.disabled = False

        # Logic for disabling/enabling the left button
        if self.page >= len(pokemons):
            self.right_button.disabled = True
        else:
            self.right_button.disabled = False

    async def update(self,interaction,pokemons):
        for item in self.give_buttons_list:
            self.remove_item(item)
        for item in self.edit_buttons_list:
            self.remove_item(item)
        updated_pokemon_embed = discord.Embed(title="Pokemons",color=discord.Colour.brand_green())
        displayed_pokemons = pokemons[self.page-5:self.page]
        for pokemon in displayed_pokemons:
            emoji = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            constructed_emoji = construct_emoji(emoji_id=emoji.emoji_id, emoji_name=emoji.name, animated=emoji.animated, unicode=emoji.unicode)
            label = f"{constructed_emoji}{pokemon.nickname}"
            text = f"{pokemon.attack1}\n{pokemon.attack2}\n{pokemon.attack3}\n{pokemon.attack4}\nNotes: {pokemon.description}"
            updated_pokemon_embed.add_field(name=label, value=text, inline=False)
        self.disable_and_enable_buttons(pokemons)

        if self.give_buttons:
            print("Creating give buttons")
            self.create_give_buttons(pokemons)
        if self.edit_buttons:
            print("Creating edit buttons")
            self.create_edit_buttons(pokemons)

        await interaction.response.edit_message(embed=updated_pokemon_embed,view=self)



class TakeView(discord.ui.View):
    def __init__(self,user_data):
        super().__init__()
        self.user_data = user_data
        self.first_pokemon_button()
        self.second_pokemon_button()
        self.third_pokemon_button()

    def first_pokemon_button(self):
        pokemon_id = self.user_data.first_pokemon_id
        button = NotImplemented
        label = ""
        if not pokemon_id:
            label = "No pokemon"
            button = discord.ui.Button(label=label, style=discord.ButtonStyle.blurple)
        else:
            pokemon_data = session.query(Pokemon).filter_by(id=pokemon_id).first()
            emoji_data = session.query(Emoji).filter_by(id=pokemon_data.emoji_id).first()
            emoji = None
            if emoji_data.unicode:
                emoji = str(emoji_data.name)
            else:
                emoji = discord.PartialEmoji(name=emoji_data.name,id=emoji_data.emoji_id,animated=emoji_data.animated)
            label = f"{pokemon_data.nickname}"
            button = discord.ui.Button(emoji=emoji,label=label,style=discord.ButtonStyle.blurple)
        async def callback(interaction:discord.Interaction,b=button):
            self.user_data.first_pokemon_id = None
            session.commit()
            await self.update(interaction)

        button.callback = callback
        self.add_item(button)
    def second_pokemon_button(self):
        pokemon_id = self.user_data.second_pokemon_id
        button = NotImplemented
        label = ""
        if not pokemon_id:
            label = "No pokemon"
            button = discord.ui.Button(label=label,style=discord.ButtonStyle.blurple)
        else:
            pokemon_data = session.query(Pokemon).filter_by(id=pokemon_id).first()
            emoji_data = session.query(Emoji).filter_by(id=pokemon_data.emoji_id).first()
            emoji = None
            if emoji_data.unicode:
                emoji = str(emoji_data.name)
            else:
                emoji = discord.PartialEmoji(name=emoji_data.name, id=emoji_data.emoji_id, animated=emoji_data.animated)
            label = f"{pokemon_data.nickname}"
            button = discord.ui.Button(emoji=emoji,label=label,style=discord.ButtonStyle.blurple)
        async def callback(interaction:discord.Interaction,b=button):
            self.user_data.second_pokemon_id = None
            session.commit()
            await self.update(interaction)


        button.callback = callback
        self.add_item(button)
    def third_pokemon_button(self):
        pokemon_id = self.user_data.third_pokemon_id
        label = ""
        button = NotImplemented
        if not pokemon_id:
            label = "No pokemon"
            button = discord.ui.Button(label=label,style=discord.ButtonStyle.blurple)
        else:
            pokemon_data = session.query(Pokemon).filter_by(id=pokemon_id).first()
            emoji_data = session.query(Emoji).filter_by(id=pokemon_data.emoji_id).first()
            emoji = None
            if emoji_data.unicode:
                emoji = str(emoji_data.name) # This is for constructing unicode emojis in buttons
            else:
                emoji = discord.PartialEmoji(name=emoji_data.name, id=emoji_data.emoji_id, animated=emoji_data.animated) # This is for constructing custom emojis in buttons
            label = f"{pokemon_data.nickname}"
            button = discord.ui.Button(emoji=emoji,label=label,style=discord.ButtonStyle.blurple)
        async def callback(interaction:discord.Interaction,b=button):
            self.user_data.third_pokemon_id = None
            session.commit()
            await self.update(interaction)

        button.callback = callback
        self.add_item(button)
    async def update(self,interaction):
        self.user_data = session.query(User).filter_by(user_id=self.user_data.user_id).first()
        #content = f"Choose the pokemon you want to take from {self.user_data.user_name}"

        self.clear_items()
        self.first_pokemon_button()
        self.second_pokemon_button()
        self.third_pokemon_button()

        await interaction.response.edit_message(view=self)


class AdminCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.role_name = data["pokemon_handler_role"]

    @app_commands.command(name="create-pokemon",description="Used for creating new pokemons, all fields are required except misc.")
    @app_commands.describe(nickname="nickname",emoji="icon",attack1="attack 1",attack2="attack 2",attack3="attack 3",attack4="attack 4",misc="misc")
    async def create_pokemon(self,interaction: discord.Interaction,nickname: str,emoji: str,attack1: str,attack2: str,attack3: str,attack4: str,misc: str = ""):
        required_role = discord.utils.get(interaction.guild.roles,name=self.role_name)
        if required_role not in interaction.user.roles: # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        guild_id = interaction.guild.id
        new_pokemon = None
        final_emoji = None
        print("Validating custom emoji")
        custom_emoji_data = is_emoji_custom(emoji)
        print(custom_emoji_data)
        if custom_emoji_data: #Is the emoji custom
            emoji_name = custom_emoji_data[0]
            emoji_id = custom_emoji_data[1]
            animated = custom_emoji_data[2]
            if not emoji_already_created(str(emoji_id)):
                print("Emoji not created yet, creating the emoji...")
                custom_emoji = emoji_creation(emoji_id=str(emoji_id), name=emoji_name, animated=animated,
                                       guild_id=guild_id, unicode=False)
                final_emoji = custom_emoji
            else:
                print("Fetching the existing emoji")
                custom_emoji = session.query(Emoji).filter_by(emoji_id=str(emoji_id)).first()
            new_pokemon = pokemon_creation(nickname=nickname, emoji_id=custom_emoji.id,
                                               attack1=attack1, attack2=attack2, attack3=attack3, attack4=attack4,
                                               description=misc)
            final_emoji = custom_emoji
        else: # If it isn't a custom emoji, take the normal emoji
            print("Creating unicode emoji")
            unicode_emoji = session.query(Emoji).filter_by(name=emoji).first()
            if not unicode_emoji:
                unicode_emoji = emoji_creation(emoji_id=None, name=emoji, animated=False,guild_id=None, unicode=True)
            new_pokemon = pokemon_creation(nickname=nickname, emoji_id=unicode_emoji.id,
                                           attack1=attack1, attack2=attack2, attack3=attack3, attack4=attack4,
                                           description=misc)
            final_emoji = unicode_emoji
        print(final_emoji)


        creation_embed = discord.Embed(title="Pokemon created",color=discord.Colour.brand_green())
        creation_embed.add_field(name="Nickname ",value=new_pokemon.nickname)

        created_emoji = construct_emoji(emoji_name=final_emoji.name,emoji_id=final_emoji.emoji_id,animated=final_emoji.animated,unicode=final_emoji.unicode)
        print(created_emoji)
        creation_embed.add_field(name="Emoji", value=created_emoji)

        creation_embed.add_field(name="attack1",value=new_pokemon.attack1,inline=False)
        creation_embed.add_field(name="attack2",value=new_pokemon.attack2,inline=False)
        creation_embed.add_field(name="attack3",value=new_pokemon.attack3,inline=False)
        creation_embed.add_field(name="attack4",value=new_pokemon.attack4,inline=False)

        creation_embed.add_field(name="misc",value=new_pokemon.description,inline=False)

        await interaction.response.send_message(embed=creation_embed)
    @app_commands.command(name="give-pokemon",description="Gives the pokemons to a specified user/player")
    @app_commands.describe(user="User Ping")
    async def give_pokemon(self,interaction: discord.Interaction, user: discord.Member):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        pokemons = session.query(Pokemon).all()
        pokemon_embed = discord.Embed(title="Pokemons",color=discord.Colour.brand_green())
        first_page = pokemons[0:5]
        for pokemon in first_page:
            emoji = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            constructed_emoji = construct_emoji(emoji_id=emoji.emoji_id,emoji_name=emoji.name,animated=emoji.animated,unicode=emoji.unicode)
            label = f"{constructed_emoji}{pokemon.nickname}"
            text = f"{pokemon.attack1}\n{pokemon.attack2}\n{pokemon.attack3}\n{pokemon.attack4}\nNotes: {pokemon.description}"
            pokemon_embed.add_field(name=label,value=text,inline=False)
        view = PageView(pokemons,True,False,self.bot)
        await interaction.response.send_message(embed=pokemon_embed,view=view)

    @app_commands.command(name="check-player",description="Checks the users player profile and returns some data about the player")
    @app_commands.describe(user="User Ping")
    async def check_user(self,interaction:discord.Interaction,user:discord.Member):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
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
    @app_commands.command(name="edit-pokemon",description="Allows editing a single field for a specified pokemon (chosen by clicking a button)")
    async def edit_pokemon(self,interaction: discord.Interaction):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permissions for this command")
            return
        pokemons = session.query(Pokemon).all()
        view = PageView(pokemons,False,True,self.bot)
        pokemon_embed = discord.Embed(title="Pokemons",color=discord.Colour.brand_green())
        first_page = pokemons[0:5]
        for pokemon in first_page:
            emoji = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            constructed_emoji = construct_emoji(emoji_id=emoji.emoji_id,emoji_name=emoji.name,animated=emoji.animated,unicode=emoji.unicode)
            label = f"{constructed_emoji}{pokemon.nickname}"
            text = f"{pokemon.attack1}\n{pokemon.attack2}\n{pokemon.attack3}\n{pokemon.attack4}\nNotes: {pokemon.description}"
            pokemon_embed.add_field(name=label,value=text,inline=False)

        await interaction.response.send_message("Select a pokemon you want to edit",embed=pokemon_embed,view=view)


    @app_commands.command(name="multiple-edit-pokemon",description="Allows editing of multiple fields for a specified pokemon (by name)")
    @app_commands.describe(pokemon_name="Pokemon Name",new_nickname="Nickname",new_emoji="Emoji",new_attack1="Attack 1",new_attack2="Attack 2",new_attack3="Attack 3",new_attack4="Attack 4",misc="Notes")
    async def multiple_edit_pokemon(self,interaction: discord.Interaction, pokemon_name: str,new_nickname: str = "",new_emoji: str = "",new_attack1: str = "",new_attack2: str = "",new_attack3: str = "",new_attack4: str = "",misc: str = ""):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permissions for this command")
            return
        pokemon = session.query(Pokemon).filter_by(nickname=pokemon_name).first()
        if new_nickname == "": new_nickname = pokemon.nickname
        if new_emoji == "": new_emoji = pokemon.emoji_id
        if new_attack1 == "": new_attack1 = pokemon.attack1
        if new_attack2 == "": new_attack2 = pokemon.attack2
        if new_attack3 == "": new_attack3 = pokemon.attack3
        if new_attack4 == "": new_attack4 = pokemon.attack4
        if misc == "": misc = pokemon.description
        pokemon.nickname = new_nickname
        emoji = None
        try: # Try getting the custom emoji
            custom_emoji = discord.utils.get(interaction.guild.emojis,name=new_emoji)
            if not emoji_already_created(str(custom_emoji.id)):
                print("Emoji not created yet")
                custom_emoji = emoji_creation(emoji_id=str(custom_emoji.id), name=custom_emoji.name, animated=custom_emoji.animated,
                                       guild_id=custom_emoji.guild_id, unicode=False)
                emoji = custom_emoji
            else:
                print("Fetching emoji")
                custom_emoji = session.query(Emoji).filter_by(emoji_id=str(custom_emoji.id)).first()
                emoji = custom_emoji
        except: # If it isn't a custom emoji, take the normal emoji
            emoji_exist = session.query(Emoji).filter_by(name=new_emoji).first()
            if emoji_exist:
                emoji = emoji_exist
            else:
                unicode_emoji = emoji_creation(emoji_id=None, name=new_emoji, animated=False,guild_id=None, unicode=True)
                emoji = unicode_emoji
        pokemon.emoji_id = emoji.id
        pokemon.attack1 = new_attack1
        pokemon.attack2 = new_attack2
        pokemon.attack3 = new_attack3
        pokemon.attack4 = new_attack4
        pokemon.description = misc
        session.commit()

        edit_embed = discord.Embed(title="Pokemon Edited",color=discord.Colour.brand_green())
        edit_embed.add_field(name="Nickname ",value=pokemon.nickname)

        edited_emoji = construct_emoji(emoji_name=emoji.name,emoji_id=emoji.emoji_id,animated=emoji.animated,unicode=emoji.unicode)
        print(edited_emoji)
        edit_embed.add_field(name="Emoji", value=edited_emoji)

        edit_embed.add_field(name="attack1",value=pokemon.attack1,inline=False)
        edit_embed.add_field(name="attack2",value=pokemon.attack2,inline=False)
        edit_embed.add_field(name="attack3",value=pokemon.attack3,inline=False)
        edit_embed.add_field(name="attack4",value=pokemon.attack4,inline=False)

        edit_embed.add_field(name="misc",value=pokemon.description,inline=False)

        await interaction.response.send_message(embed=edit_embed)


    @app_commands.command(name="set-image-for-player",description="Sets the profile image for the specified player")
    @app_commands.describe(user="User Ping")
    async def set_image_for_player(self,interaction: discord.Interaction, user: discord.Member):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permissions for this command")
            return
        user_data = session.query(User).filter_by(user_id=user.id).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        await interaction.response.send_message("Send the image now")
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel and msg.attachments

        try:

            msg = await self.bot.wait_for("message", timeout=20, check=check)
            profile_image = msg.attachments[0]
            print(profile_image, type(profile_image))
            user_data.image_url = str(profile_image)
            session.commit()
            await interaction.followup.send(f"Your image was stored. {profile_image.url}")
        except asyncio.TimeoutError:
            await interaction.followup.send("It took you too long to send the image")
    @app_commands.command(name="remove-image-for-player",description="Removes the profile image for the specified player")
    @app_commands.describe(user="User Ping")
    async def remove_image_for_player(self,interaction: discord.Interaction, user: discord.Member):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permissions for this command")
            return
        user_data = session.query(User).filter_by(user_id=user.id).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        user_data.image_url = None
        session.commit()
        await interaction.response.send_message("Successfully removed users profile image.")


    @app_commands.command(name="take-pokemon",description="Takes the pokemon from the player (doesn't  delete the pokemon)")
    @app_commands.describe(user="User Ping")
    async def take_pokemon(self,interaction:discord.Interaction,user: discord.Member):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        guild = interaction.guild
        user_server = await guild.fetch_member(int(user.id))
        user_server_name = user_server.display_name
        user_data = session.query(User).filter_by(user_id=user.id).first()
        if not user_data:
            await interaction.response.send_message("This user doesn't have a player created.")
            return
        view = TakeView(user_data)
        await interaction.response.send_message(f"Choose the pokemon you want to take from {user_server_name}",view=view,ephemeral=True)
    @app_commands.command(name="all-pokemons",description="Shows all the available pokemons")
    async def all_pokemons(self,interaction: discord.Interaction):
        required_role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if required_role not in interaction.user.roles:  # This is less secure, but if not used widely, it should be fine
            await interaction.response.send_message("You don't have permissions for this command")
            return
        pokemons = session.query(Pokemon).all()
        pokemon_embed = discord.Embed(title="Pokemons",color=discord.Colour.brand_green())
        first_page = pokemons[0:5]
        for pokemon in first_page:
            emoji = session.query(Emoji).filter_by(id=pokemon.emoji_id).first()
            constructed_emoji = construct_emoji(emoji_id=emoji.emoji_id,emoji_name=emoji.name,animated=emoji.animated,unicode=emoji.unicode)
            label = f"{constructed_emoji}{pokemon.nickname}"
            text = f"{pokemon.attack1}\n{pokemon.attack2}\n{pokemon.attack3}\n{pokemon.attack4}\nNotes: {pokemon.description}"
            pokemon_embed.add_field(name=label,value=text,inline=False)
        view = PageView(pokemons,False,False,self.bot)
        await interaction.response.send_message(embed=pokemon_embed,view=view)

    """
    @app_commands.command(name="test")
    async def test(self,interaction:discord.Interaction):
        emoji = construct_emoji(emoji_name="ZGeconomy",emoji_id=1397968517328015521,animated=False,unicode=False)
        await interaction.response.send_message(emoji)
    """

    @app_commands.command(name="admin-help")
    async def admin_help(self,interaction:discord.Interaction):
        required_role = discord.utils.get(interaction.guild.roles,name=self.role_name)
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permissions for this command")
            return
        help_embed = discord.Embed(title="Admin Help",description="Shows all the admin commands and what they do.", color=discord.Color.brand_green())
        help_embed.add_field(name="create-pokemon",value="Used for creating new pokemons, all fields are required except misc.",inline=False)
        help_embed.add_field(name="check-player",value="Checks the users player profile and returns some data about the player",inline=False)
        help_embed.add_field(name="create-player",value="Creates the player for the user",inline=False)
        help_embed.add_field(name="all-pokemons",value="Shows all the available pokemons",inline=False)
        help_embed.add_field(name="give-pokemon",value="Gives the pokemons to a specified user/player",inline=False)
        help_embed.add_field(name="multiple-edit-pokemon",value="Allows editing of multiple fields for a specified pokemon (by name)",inline=False)
        help_embed.add_field(name="edit-pokemon",value="Allows editing a single field for a specified pokemon (chosen by clicking a button)",inline=False)
        help_embed.add_field(name="take-pokemon",value="Takes the pokemon from the player (doesn't  delete the pokemon)",inline=False)
        help_embed.add_field(name="set-image-for-player", value="Sets the profile image for the specified player", inline=False)
        help_embed.add_field(name="remove-image-for-player",value="Removes the profile image for the specified player",inline=False)
        help_embed.add_field(name="sync_bot",value="Used for syncing the bot (used for development purposes)",inline=False)

        await interaction.response.send_message(embed=help_embed,ephemeral=True)
        
#@app_commands.describe(id="ID",title="title",content="content",checkmark="check mark")
#async def edit_a_wish(interaction:discord.Interaction,id: str, title: str = "optional", content: str = "optional", checkmark: bool = False):


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))