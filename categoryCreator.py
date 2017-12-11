from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
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


# Menu for UrbanBurger
category1 = Category(name="")

session.add(restaurant1)
session.commit()

item1 = Item(name="", description="",category=category1)

session.add(menuItem2)
session.commit()


item2 = Item(name="", description="",category=category1)

session.add(menuItem1)
session.commit()

item3 = Item(name="", description="",category=category1)

session.add(menuItem2)
session.commit()

item4 = Item(name="", description="",category=category1)

session.add(menuItem3)
session.commit()

item5 = Item(name="", description="",category=category1)

session.add(menuItem4)
session.commit()


# Menu for Super Stir Fry
category2 = Category(name="")

session.add(category2)
session.commit()


item1 = Item(name="", description="",category=category2)

session.add(item1)
session.commit()

item2= Item(name="", description="",category=category2)

session.add(item2)
session.commit()

item3 = Item(name="", description="",category=category2)

session.add(item3)
session.commit()

item4 = Item(name="", description="",category=category2)

session.add(item4)
session.commit()

item5 = Item(name="", description="",category=category2)

session.add(item5)
session.commit()


# Menu for Panda Garden
category3 = Category(name="")

session.add(category3)
session.commit()


item1 = Item(name="", description="",category=category3)

session.add(item1)
session.commit()

item2 = Item(name="", description="",category=category3)

session.add(item2)
session.commit()

item3 = Item(name="", description="",category=category3)

session.add(item3)
session.commit()

item4 = Item(name="", description="",category=category3)

session.add(item4)
session.commit()

item5 = Item(name="", description="",category=category3)

session.add(item5)
session.commit()


# Menu for Thyme for that
category4 = Category(name="")

session.add(category4)
session.commit()


item1 = Item(name="", description="", category=category4)

session.add(item1)
session.commit()

item2 = Item(name="", description="", category=category4)

session.add(item2)
session.commit()

item3 = Item(name="", description="", category=category4)

session.add(item3)
session.commit()

item4 = Item(name="", description="", category=category4)

session.add(item4)
session.commit()

item5 = Item(name="", description="", category=category4)

session.add(item5)
session.commit()


# Menu for Tony's Bistro
category5 = Category(name="")

session.add(category5)
session.commit()


item1 = Item(name="", description="", category=category5)

session.add(menuItem1)
session.commit()

item2 = Item(name="", description="", category=category5)

session.add(item2)
session.commit()

item3 = Item(name="", description="", category=category5)

session.add(item3)
session.commit()

item4 = Item(name="", description="", category=category5)

session.add(item4)
session.commit()

item5 = Item(name="", description="", category=category5)

session.add(item5)
session.commit()


# Menu for Andala's
category6 = Category(name="")

session.add(category6)
session.commit()


item1 = Item(name="", description="", category=category6)

session.add(item1)
session.commit()

item2 = Item(name="", description="", category=category6)

session.add(item2)
session.commit()

item3 = Item(name="", description="", category=category6)

session.add(item3)
session.commit()

item4 = Item(name="", description="", category=category6)

session.add(item4)
session.commit()

item5 = Item(name="", description="", category=category6)

session.add(item5)
session.commit()





print "added menu items!"
