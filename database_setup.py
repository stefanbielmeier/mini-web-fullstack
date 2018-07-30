#Sys functions 
import sys

#SQLAlchemy import for using the database 
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

#setup class code (this is what the classes in following python code inherit from)
Base = declarative_base()

#END CONFIGURATION CODE ________________________________________ START CLASS CODE

class Restaurant(Base):
	"""tablenames have to be clarified with __tablename__ to let SQLAlchemy know what it is
	Restaurant extends Base
	SYNTAX: __tablename__ = 'something_something'
	"""
	__tablename__ = 'restaurant'

	"""
	SYNTAX: columnName = Column(attributes, ...)
			for example could be String(250), Integer, relationship(Class), nullable = False,
			primary key = True, ForeignKey('some_table.id')
	"""

	name = Column(String(80), nullable = False)
	id = Column (Integer, primary_key = True)


		
class MenuItem(Base):
	"""Watch out for how the nomenclature for the tables is
	Also: table Name and column names are lowercase and with underscores! """

	__tablename__ = 'menu_item'
	
	name = Column(String(80), nullable = False)
	id = Column (Integer, primary_key = True)
	course = Column(String(250))
	description = Column(String(250))
	price = Column(String(8)) #basic Database 101... never a price with a String but whatever
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))

	# ==> Connect the two tables
	restaurant = relationship(Restaurant)


#END CLASS CODE _____________________________ START MAPPER CODE

## E
#Creates a file that is our database. Instead of sqlite we can use PostgreSQL or MySQL.
engine = create_engine('sqlite:///restaurantmenu.db')

#goes in the database file & adds the tables above to it.
Base.metadata.create_all(engine)