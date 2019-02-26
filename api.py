# encoding: utf-8
from eve import Eve
from eve.auth import BasicAuth # For authentication
from flask import request # Deal with request
from bson import ObjectId # To convert _id field from string to ObjectId (for MongoDB)

class Authenticate(BasicAuth):
	
	def attempt(self, username, password):
		# Checks username and password
		user = app.data.driver.db['user']
		user = user.find_one({'username': username, 'pwd': password})
		return user

	def find_by_field(self, collection, field, value):
		# Finds _id value as string into the collection
		aux = app.data.driver.db[collection]
		return aux.find_one({field: value })

	def find_where(self, collection, field, value):
		# Finds documents from collection where field matches value
		aux = app.data.driver.db[collection]
		return aux.find({field: value })

	def check_auth(self, user, password, allowed_roles, resource, method):
		if resource == 'user':
			# User must be authenticated
			user_ = self.attempt(user,password)
			if user_:
				# Get request as json
				req = request.json
				# Split url into list
				path = request.path
				if path[-1] == '/':
					path = path[:-1]
				# path[2] is for item in /user/<item>
				path = path.split('/')
				# Get schema for adding filters
				schema = app.config['DOMAIN'][resource]
				# Check method
				if method in ['PATCH','PUT','DELETE']:
					# Check if url is for item using len(path)
					# Then check if user is on its own user endpoint
					if len(path)>2 and path[2] == str(user_['_id']):
						return True
					return False
				if method in ['GET']:
					# HIDE PASSWORD FIELD
					schema['datasource']['projection'] = {'username':1}
					# Check if url is for item using len(path)
					# Then check if user is on its own user endpoint
					if len(path)>2 and path[2] == str(user_['_id']):
						# If so, show password
						schema['datasource']['projection'] = {'username':1,'pwd':1}
					return True
			else:
				if method == 'POST':
					# Not authenticated can create new users
					return True
				return False
		elif resource == 'conversation':
			# User must be authenticated
			user_ = self.attempt(user,password)
			if user_:
				req = request.json
				schema = app.config['DOMAIN'][resource]
				if method == 'POST':
					# Only create for himself
					who = self.find_by_field('user', '_id', ObjectId(req['user']))
					# And for conversations where he is part of adms
					adms = [ a['_id'] for a in req['adms']]
					# Check if its for him and if he is in adms
					if who == user_ and req['user'] in adms:
						return True
				elif method == 'GET':
					# Only can read the conversations in wich the authenticated user is a member
					schema['datasource']['filter'] = {"$or":[{'users._id': user_['_id']}, {'adms._id': user_['_id']}]}
				else:
					# Only conversation authenticated adms can PUT PATCH or DELETE
					schema['datasource']['filter'] = {'adms': user_['_id']}
				return True
			return False
		elif resource == 'messages':
			# User must be authenticated
			user_ = self.attempt(user,password)
			if user_:
				if method in ['POST','DELETE']:
					# Get request as json
					req = request.json
					# His _id must be the same as 'from' field
					who = self.find_by_field('user','_id', ObjectId(req['from']))
					if who:
						# So as he must be in the conversation
						conversation = self.find_by_field('conversation','_id', ObjectId(req['to']))
						# As user or adm
						if conversation:
							users = [ a['_id'] for a in conversation['users']]
							adms = [ a['_id'] for a in conversation['adms']]
							if who == user_ and (ObjectId(req['from']) in adms or ObjectId(req['from']) in users):
								return True
				elif method in ['PATCH']:
					# Get request as json
					req = request.json
					# He cannot change who sent to who and what
					if any(r in ['from','to','content'] for r in req):
						return False
					# Split url into list
					path = request.path
					if path[-1] == '/':
						path = path[:-1]
					# path[2] is for item in /message/<item>
					path = path.split('/')
					# Check if its a item path
					if len(path)>2 and path[2] == str(user_['_id']):
						# Search target message
						who = self.find_by_field('messages','_id', ObjectId(path[2]))
						# Check if it got found and if its emmiter is the user
						if who and who['from'] == user_['_id']:
							return True
					return False
				elif method in ['GET']:
					# Filter messages wich he sent, or recieve from groups
					filter_4user = {"$or":[{'from': user_['_id']}]}
					# From conversations in wich user is member
					conversations = self.find_where('conversation','users._id', user_['_id'])
					if conversations:
						# Get conversations ids
						conversations = [a['_id'] for a in conversations]
						if conversations:
							# Add operator to check if 'to' field value is in conversations _id list
							filter_4user["$or"].append({'to': {'$in':conversations}})
					# From conversations in wich user is ADM
					conversations = self.find_where('conversation','adms._id', user_['_id'])
					if conversations:
						# Get conversations ids
						conversations = [a['_id'] for a in conversations]
						if conversations:
							# Add operator to check if 'to' field value is in conversations _id list
							filter_4user["$or"].append({'to': {'$in':conversations}})
					# From conversations in wich user is its creator
					conversations = self.find_where('conversation','user', user_['_id'])
					if conversations:
						# Get conversations ids
						conversations = [a['_id'] for a in conversations]
						if conversations:
							# Add operator to check if 'to' field value is in conversations _id list
							filter_4user["$or"].append({'to': {'$in':conversations}})
					# Get schema for add filters
					schema = app.config['DOMAIN'][resource]
					# Attach filter to results
					schema['datasource']['filter'] = filter_4user
					return True
			return False
		else:
			# If in / then show API methods
			return True

if __name__ == '__main__':
	app = Eve(auth=Authenticate)
	app.run()
