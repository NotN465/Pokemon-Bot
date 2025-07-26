from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,relationship
from models import User,Pokemon,Emoji

engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

def user_already_created(user_discord_id: str):
    user = session.query(User).filter_by(user_id=str(user_discord_id)).first()
    return bool(user)

def emoji_already_created(emoji_id: str):
    emoji = session.query(Emoji).filter_by(emoji_id=str(emoji_id)).first()
    return bool(emoji)

def user_creation(user_discord_id,user_name,pokemon1_id,pokemon2_id,pokemon3_id):
    new_user = User(user_id=user_discord_id,user_name=user_name,
                    first_pokemon_id=pokemon1_id,
                    second_pokemon_id=pokemon2_id,
                    third_pokemon_id=pokemon3_id)
    session.add(new_user)
    session.commit()
    return new_user

def emoji_creation(emoji_id,name,animated,guild_id):
    new_emoji = Emoji(emoji_id=emoji_id,name=name,animated=animated,guild_id=guild_id)
    session.add(new_emoji)
    session.commit()
    return new_emoji

def pokemon_creation(nickname,emoji_id,attack1,attack2,attack3,attack4,description):
    new_pokemon = Pokemon(nickname=nickname,emoji_id=emoji_id,
                          attack1=attack1,attack2=attack2,
                          attack3=attack3,attack4=attack4,
                          description=description)
    session.add(new_pokemon)
    session.commit()
    return new_pokemon
def construct_emoji(emoji_name,emoji_id,animated: bool):
    return f"<{'a' if animated else ''}:{emoji_name}:{emoji_id}>"

