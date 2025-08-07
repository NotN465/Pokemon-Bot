import re

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,relationship
from sqlalchemy import Column, Integer, String,ForeignKey,Boolean

engine = create_engine("sqlite:///database.db", echo=False)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(String,unique=True)
    user_name = Column(String)
    image_url = Column(String)

    first_pokemon_id = Column(Integer,ForeignKey("pokemon.id"))
    second_pokemon_id = Column(Integer,ForeignKey("pokemon.id"))
    third_pokemon_id = Column(Integer,ForeignKey("pokemon.id"))

    first_pokemon = relationship("Pokemon",foreign_keys=[first_pokemon_id])
    second_pokemon = relationship("Pokemon",foreign_keys=[second_pokemon_id])
    third_pokemon = relationship("Pokemon",foreign_keys=[third_pokemon_id])


class Pokemon(Base):
    __tablename__ = 'pokemon'
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String)
    emoji_id = Column(Integer,ForeignKey('emoji.id'))
    emoji = relationship("Emoji", back_populates="pokemon")
    attack1 = Column(String)
    attack2 = Column(String)
    attack3 = Column(String)
    attack4 = Column(String)
    description = Column(String)


class Emoji(Base):
    __tablename__ = 'emoji'
    id = Column(Integer, primary_key=True, index=True)
    unicode = Column(Boolean)
    emoji_id = Column(String)
    name = Column(String)
    animated = Column(Boolean)
    guild_id = Column(String)

    pokemon = relationship("Pokemon",back_populates="emoji")
# emoji = session.query(Emoji).filter_by(id=10).first()
# session.delete(emoji)
# session.commit()
"""
emoji = "<:ZGeconomy:1397968517328015521>"
pattern = r"<:([a-zA-Z0-9_]+):(\d+)>"
custom_emoji = re.match(pattern,emoji)
if custom_emoji:
    name = custom_emoji.group(1)
    emoji_id = custom_emoji.group(2)
    print(f"Name: {name}, ID: {emoji_id}")
"""


Base.metadata.create_all(bind=engine)
