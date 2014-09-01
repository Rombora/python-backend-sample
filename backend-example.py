#!/usr/bin/env python
"""
Licensed under the MIT Licence, Copyright (c) 2014 Sinch / Rebtel Networks AB

"""
import tornado.ioloop
import tornado.web
from tornado.web import Finish
from datetime import datetime
import json
import uuid
import hmac
import hashlib
import base64

#App key + secret
APPLICATION_KEY = 'e15e9421-2f30-411b-bd49-00bd5f815e36'
APPLICATION_SECRET = 'AINnd5S7ZEeRItNcYjajaA=='

userBase = dict()

class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('pong')

class RestResource(tornado.web.RequestHandler):
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")

	def write_error(self, status_code, **kwargs):
		data = {}
		for key, value in kwargs.iteritems():
			data[key] = value
		try:
			del data['exc_info']
		except: 
			pass

		self.write(json.dumps(data))
		self.set_status(status_code)
		raise Finish()

class RegisterHandler(RestResource):
	def post(self):
		user = json.loads(self.request.body)

		if 'username' not in user:
			self.write_error(400, code=40001, message='username not found')
		if 'password' not in user:
			self.write_error(400, code=40002, message='password not found')
		if user['username'] in userBase: 
			self.write_error(400, code=40003, message='user already registered')

		salt = uuid.uuid4().hex	
		userBase[user['username']] = salt, hashlib.sha256(salt + user['password'] + '31337 salted').hexdigest()

		print ('Created user, now the user base is:')
		for name in userBase:
			print ('\t' + name + '\t' + userBase[name][1])

class LoginHandler(RestResource):
	def post(self):
		user = json.loads(self.request.body)

		if 'username' not in user:
			self.write_error(400, code=40001, message='username not found')
		if 'password' not in user:
			self.write_error(400, code=40002, message='password not found')
		if user['username'] not in userBase: 
			self.write_error(400, code=40004, message='user not registered')

		salt = userBase[user['username']][0]
		correctPassHash = userBase[user['username']][1]
		candidatePassHash = hashlib.sha256(salt + user['password'] + '31337 salted').hexdigest()

		if candidatePassHash != correctPassHash:
			self.write_error(401, code=40100, message='incorrect password')
		elif candidatePassHash == correctPassHash: #Correct password

			#Implementation of http://www.sinch.com/docs/rest-apis/api-documentation/#Authorization
			userTicket = {
				'identity': {'type': 'username', 'endpoint': user['username']},
				'applicationKey': APPLICATION_KEY,
				'created': datetime.utcnow().isoformat()
			}

			userTicketJson = json.dumps(userTicket).replace(" ", "")
			userTicketBase64 = base64.b64encode(userTicketJson)

			#TicketSignature = Base64 ( HMAC-SHA256 ( ApplicationSecret, UTF8 ( UserTicketJson ) ) )
			digest = hmac.new(base64.b64decode(APPLICATION_SECRET), msg=userTicketJson, digestmod=hashlib.sha256).digest()
			signature = base64.b64encode(digest)

			#UserTicket = TicketData + ":" + TicketSignature
			signedUserTicket = userTicketBase64+':'+signature

			returnObj = {
				'userTicket': signedUserTicket
			}

			self.write(json.dumps(returnObj))

backend = tornado.web.Application([
    (r"/ping", PingHandler),
    (r"/register", RegisterHandler),
    (r"/login", LoginHandler),
])

if __name__ == "__main__":
    backend.listen(2048)
    tornado.ioloop.IOLoop.instance().start()

