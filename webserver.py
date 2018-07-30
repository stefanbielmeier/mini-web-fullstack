"""this Code is different from the simple webserver. Here we'll have to tell our server
	and our Handler, how HTTP GET- and POST-Requests should be handled to our
	current directory the server is in! 

	BaseHTTPRequestHandler is not able to handle any requests itself. 
	It must be instanced to handle each Request (GET, POST or HEAD)
"""

#Import Server
from http.server import HTTPServer, BaseHTTPRequestHandler

#Common Gateway Interface Support Group, for scripts!
import cgi
import os.path

#Database and ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#Set up database
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
#easier name to work with: session, functions as a staging zone between what we add to the session, and what gets
#to the database
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	"""docstring for webserverHandler"""

	#handles all the GET requests the server receives.
	#overrides the method in the BaseHTTPRequestHandler class
	def do_GET(self):
		'''
		pattern matching plan: only looks for the ending of the requested URL path
		respond with the requested document to the client
		'''
		try:
			#Catch Initial Request
			if self.path.endswith("/restaurants"):
				#If Path hello was requested: send response for successful GET Request (200)
				self.send_response(200)
				#indicates that the server replies with text in the form of HTML to the client
				self.send_header("Content-type", "text/html; charset=utf-8")
				#indicating the end of the server HTTP headers by sending an empty line
				#MUST BE CALLED TO COMPLETE SEND HEADER
				self.end_headers() 

				restaurants = session.query(Restaurant).all()
				output = ""
				output += "<html><body>"
				for restaurant in restaurants:
					output += " <h2>{}</h2>".format(restaurant.name)
					output += "<a href='/{}/edit'>Edit Entry <br> </a>".format(restaurant.id)
					output += "<a href='/{}/delete'>Delete Entry</a>".format(restaurant.id)
					output += "<br></br>"
				output += "<br></br>"
				output += "<p> Add a new Restaurant with this link </p>"
				output += "<a href='/add'>Add New</a>"
				output += "</body></html>"
				#Transforms String into Byte Like Object that is needed for the wfile() function
				output = output.encode('utf-8') 

				#Output by writing and sending out IO.BufferedIOBase stream
				self.wfile.write(output)
				#debugging
				print (output)
				#exit if statement
				return

			#CATCHING GET Request for /add
			if self.path.endswith("/add"):
				self.send_response(200)
				self.send_header("Content-type", "text/html; charset=utf-8")
				self.end_headers() 

				output = ""
				output += "<html><body>"
				output += "<h2>Enter and submit the new Restaurant name</h2>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants'> <p>New Restaurant:</p> <input name="new_restaurant" type="text" ><input type="submit" value="Submit"> </form>'''
				output += "</body></html>"



				#Transforms String into Byte Like Object that is needed for the wfile() function
				output = output.encode('utf-8') 

				self.wfile.write(output)
				print(output)
				return

			#CATCHING GET Request for /edit
			if self.path.endswith("/edit"):
				self.send_response(200)
				self.send_header("Content-type", "text/html; charset=utf-8")
				self.end_headers()

				#Do Send out Data to POST Request:
				#Restaurant ID and the new name.
				restaurant_id = os.path.split(self.path)[0]
				restaurant_id = restaurant_id[1:]


				# Action Attribute in Form tag will determine the Path that we can Catch in the Post Request!
				# If we want to get Data from the path form the GET request in the Post request and not having to send two 
				#values with a hidden input tag, we will have to define the Action path including the
				# ID of the Restaurant. 
				output = ""
				output += "<html><body>"
				output += "<h2>Enter and submit the new Restaurant name</h2>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants'> 
					<p>New Name for Restaurant:</p> 
					<input name="new_restaurant_name" type="text">
					<input type="hidden" name="restaurant_id" value="{}">
					<input type="submit" value="Submit">
				</form>'''.format(restaurant_id)
				output += "</body></html>"

				#Transforms String into Byte Like Object that is needed for the wfile() function
				output = output.encode('utf-8') 

				self.wfile.write(output)
				print(output)
				return

			#Get Request for Delete!
			if self.path.endswith("/delete"):
				self.send_response(200)
				self.send_header("Content-type", "text/html; charset=utf-8")
				self.end_headers()

				#Do Send out Data to POST Request:
				#Restaurant ID and the new name.
				restaurant_id = os.path.split(self.path)[0]
				restaurant_id = restaurant_id[1:]

				restaurant_name = session.query(Restaurant).filter_by(id = "{}".format(restaurant_id)).one().name

				output = ""
				output += "<html><body>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants'> 
					<h2>Are you sure you would like to delete {} ?</p> 
					<input type="hidden" name="deletion_id" value="{}">
					<input type="submit" value="Delete">
				</form>'''.format(restaurant_name, restaurant_id)
				output += "</body></html>"

				#Transforms String into Byte Like Object that is needed for the wfile() function
				output = output.encode('utf-8') 

				self.wfile.write(output)
				print(output)
				return

		#If Request is not to path "/hello" or output can't be written / sent to client
		except IOError:	
			self.send_error(404, "File Not Found %s" % self.path)
		


	def do_POST(self):
		try:
			#response code for successful post

			#Should be further down only when the POST ACTUALLY Was successful.
			self.send_response(301)
			#has to be added like before
			#let the browser know that we have UTF 8. Output is already UTF 8
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
 
			'''
			important security issue. Client passes information in forms that we do not
			know about. Never pass this information into a shell script, since it can 
			and will be hacked.
			If you have to:
			Passed-on String should only contain Numbers, Letters, Dashes, Underscores
			and Periods
			'''

			#CGI Script is used to process user input submitted through an HTML <FORM> or 
			#<ISINDEX> element/tag.
			# A form can be an input field, choosing an option field, etc.

			ctype, pdict = cgi.parse_header(self.headers['Content-type'])
			#pdict has to be encoded in byte string format for parse_multipart
			pdict['boundary'] = pdict['boundary'].encode('utf-8')
			if  ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				#messagecontent gives out a list, so we want the first (and only) message.
				#Also, has to be decoded to get a regular string instead of a byte string
				#retrieves new_restaurant and the new name, depending on what's been changed
			print(fields)

			#Add new Restaurant if POST Request is for adding a New Restaurant
			if fields.get('new_restaurant') != None:
				messagecontent = fields.get('new_restaurant')[0].decode()
				#Add new Restaurant from Form Data to Database	
				newRestaurant = Restaurant(name = messagecontent)
				session.add(newRestaurant)
				session.commit()

			#change the name of a restaurant
			if fields.get('new_restaurant_name') != None:
				new_name = fields.get('new_restaurant_name')[0].decode()
				restaurant_id = fields.get('restaurant_id')[0].decode()
				print(self.path)
				toBeChanged = session.query(Restaurant).filter_by(id = '{}'.format(restaurant_id)).one()
				toBeChanged.name = new_name
				session.add(toBeChanged)
				session.commit()

			if fields.get('deletion_id') != None:
				toBeDeleted_id = fields.get('deletion_id')[0].decode()
				toBeDeleted = session.query(Restaurant).filter_by(id = '{}'.format(toBeDeleted_id)).one()
				session.delete(toBeDeleted)
				session.commit()


			
			#Retrieve entire List of Restaurants, inluding the new one
			restaurants = session.query(Restaurant).all()
			output = ""
			output += "<html><body>"
			for restaurant in restaurants:
				output += " <h2>{}</h2>".format(restaurant.name)
				output += "<a href='/{}/edit'>Edit Entry  <br> </a>".format(restaurant.id)
				output += "<a href='/{}/delete'>Delete Entry</a>".format(restaurant.id)
				output += "<br></br>"
			output += "<br></br>"
			output += "<p> Add a new Restaurant with this link </p>"
			output += "<a href='/add'>Add New</a>"
			output += "</body></html>"

			self.wfile.write(output.encode())
			print(output)

			''' A Redirect should be added once the POST request on the original site has been completed
			The POST Request itself should be done at the same path as the GET request!
			For this, the ACTION attribute in the FORM tag in HTML in the GET Request cannot
			be forwarding to /restaurants already!

			self.send_header('Location', '/restaurants')

			Apart from this, the headers as well as the notification of a successful GET Request 
			shall only be sent AFTER the POST Request Backend Code has been executed.
			'''
			
		except:
			print("Error!")

def main():
	try:
		port = 8080
		server = HTTPServer(("", port), webserverHandler)
		print("Web server running on port %s" %port)
		#constantly listening server until server is shutdown
		server.serve_forever()

	#closing server on Keyboard Interrupt which is built in into Python	
	except KeyboardInterrupt:
		print ("Keyboard interrupt recieved, stopping web server")
		server.socket.close()


if __name__ == '__main__':
	main()