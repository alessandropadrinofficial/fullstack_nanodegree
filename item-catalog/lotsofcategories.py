from sqlalchemy.orm import sessionmaker
from catalog_db import Base, Category, Item, User, engine

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


user = User(name="Alessandro", email="alessandro.padrin.sam@gmail.com")
session.add(user)
session.commit()


cat = Category(name="Baseball", description="Sport with a ball and baseball bats")
session.add(cat)
session.commit()

it = Item(name="Babe Ruth ball", description="Original ball to play baseball",
            category=cat, user=user)
session.add(it)
session.commit()

it = Item(name="Babe Ruth baseball bat", description="Original baseball bat",
            category=cat, user=user)
session.add(it)
session.commit()


cat = Category(name="Basketball", description="Sport with a ball and a basket")
session.add(cat)
session.commit()

it= Item(name="Jordan ball", description="Original ball to play basketball", category=cat,
            user=user)
session.add(it)
session.commit()

it = Item(name="Air Jordan", description="Nike Shoes", category=cat,
            user=user)
session.add(it)
session.commit()



cat= Category(name="Tennis", description="Sport with rackets and a ball")
session.add(cat)
session.commit()

it = Item(name="Roger ball", description="Original ball to play tennis", category=cat,
            user=user)
session.add(it)
session.commit()

it = Item(name="Air Roger", description="Nike shoes for tennis", category=cat,
            user=user)
session.add(it)
session.commit()
