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
    emoji_id = Column(String)
    name = Column(String)
    animated = Column(Boolean)
    guild_id = Column(String)

    pokemon = relationship("Pokemon",back_populates="emoji")


Base.metadata.create_all(bind=engine)
