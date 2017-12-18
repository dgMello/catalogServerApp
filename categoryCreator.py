from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Doug Mello", email="dmello88@gamil.com")
session.add(User1)
session.commit()

category1 = Category(user_id=1, name="Shirts")

session.add(category1)
session.commit()

item1 = Item(user_id=1, name="T-Shirt", description="Cotton & short sleeves",
    category=category1)

session.add(item1)
session.commit()


item2 = Item(user_id=1, name="Polo shirt",
    description="Short sleeves & a collar", category=category1)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Button Up", description="Long sleeve and buttons",
    category=category1)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Sleeveless shirt",
    description="Cotton & no sleeves.", category=category1)

session.add(item4)
session.commit()



category2 = Category(user_id=1, name="Pants")

session.add(category2)
session.commit()


item1 = Item(user_id=1, name="Jeans", description="Blue jeans",
    category=category2)

session.add(item1)
session.commit()

item2= Item(user_id=1, name="Kackis", description="Brown cotton pants",
    category=category2)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Shorts",
    description="Cotton and cut at the knees.", category=category2)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Parachute pants", description="Whoah!",
    category=category2)

session.add(item4)
session.commit()



category3 = Category(user_id=1, name="Hats")

session.add(category3)
session.commit()


item1 = Item(user_id=1, name="Blue hat", description="It's blue.",
    category=category3)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Red hat", description="It's red.",
    category=category3)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Green hat", description="It's green.",
    category=category3)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Black hat", description="It's black.",
    category=category3)

session.add(item4)
session.commit()


category4 = Category(user_id=1, name="Jackets")

session.add(category4)
session.commit()


item1 = Item(user_id=1, name="Jean jacket", description="It's not the 80's.",
    category=category4)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Windbreaker", description="Breaks the wind",
    category=category4)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Winter jacket", description="Warm!",
    category=category4)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Sports jacket", description="Fancy!",
    category=category4)

session.add(item4)
session.commit()



print "added category items!"
