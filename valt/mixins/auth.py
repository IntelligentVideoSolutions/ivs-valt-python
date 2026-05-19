import json
import http.client
from urllib import error, request
import time, threading


class valt_auth:
	def auth(self):
		# Authenticate to VALT server
		# Sets accesstoken value to 0 if the authentication attempt fails.
		if self.username != "None" and self.username != "" and self.username is not None and self.password != "None" and self.password != "" and self.password is not None and self.baseurl is not None:
			values = {"username": self.username, "password": self.password}
			self.logger.debug(__name__ + ": " + self.baseurl)
			self.logger.debug(__name__ + ": " + self.username)
			url = self.baseurl + 'login'
			data = self.send_to_valt(url, values=values)
			self.lastauthtime = time.time()
			if type(data).__name__ == "dict":
				self.accesstoken = data['data']['access_token']
				self.errormsg = None
				self.logger.info(__name__ + ": " + "Authenticated to VALT")
				self.version = self.getversion()
				self.major_version = self.version.split(".")[0]
				self.minor_version = self.version.split(".")[1]
				if self.major_version == "6":
					self.patch_level = self.version.split(".")[2]
				self.logger.info(__name__ + ": " + "Valt Version: " + str(self.version))
				self.reauthenticate(self.success_reauth_time)
			else:
				self.logger.error(__name__ + ": " + "Authentication FAILED")
	def reauthenticate(self, reauthtime):
		self.logger.info(__name__ + ":" + " Next authentication attempt in " + str(reauthtime) + " seconds")
		if hasattr(self, 'reauth'):
			self.reauth.cancel()
		self.reauth = threading.Timer(reauthtime, self.auth)
		self.reauth.daemon = True
		self.reauth.start()

	def changeserver(self, valt_address, valt_username, valt_password):
		if valt_address != "None" and valt_address != "" and valt_address is not None:
			self.disconnect()
			if valt_address.find("http", 0, 4) == -1:
				self.baseurl = 'http://' + valt_address + '/api/v3/'
			else:
				self.baseurl = valt_address + '/api/v3/'
		else:
			self.baseurl = None
		self.username = valt_username
		self.password = valt_password
		self.auth()

	def testconnection(self, valt_address, valt_username, valt_password):
		values = {"username": valt_username, "password": valt_password}
		params = json.dumps(values).encode('utf-8')
		if valt_address.find("http", 0, 4) == -1:
			valt_baseurl = 'http://' + valt_address + '/api/v3/'
		else:
			valt_baseurl = valt_address + '/api/v3/'
		self.logger.debug(__name__ + ": " + "Testing Connection to VALT server")
		self.logger.debug(__name__ + ": " + valt_baseurl)
		self.logger.debug(__name__ + ": " + valt_username)
		self.logger.debug(__name__ + ": " + valt_password)

		try:
			req = request.Request(valt_baseurl + 'login')
			req.add_header('Content-Type', 'application/json')
			response = request.urlopen(req, params, timeout=self.httptimeout)
		except error.HTTPError as e:
			self.logger.warning(__name__ + ": " + str(e))
			if str(e) == "HTTP Error 401: Unauthorized":
				self.testmsg = "Invalid Username or Password"
			return False
		except error.URLError as e:
			self.logger.warning(__name__ + ": " + str(e))
			self.testmsg = "Unable to Connect"
			return False
		except http.client.HTTPException as e:
			self.logger.warning(__name__ + ": " + str(e))
			self.testmsg = "Unable to Connect"
			return False
		except Exception as e:
			self.logger.warning(__name__ + ": " + str(e))
			self.testmsg = "Unable to Connect"
			return False
		else:
			return True
	@property
	def accesstoken(self):
		return self._accesstoken
	@accesstoken.setter
	def accesstoken(self,newmsg):
		self._accesstoken = newmsg
		for callback in self._accesstoken_observers:
			callback(self._accesstoken)
	def bind_to_accesstoken(self,callback):
		self._accesstoken_observers.append(callback)
