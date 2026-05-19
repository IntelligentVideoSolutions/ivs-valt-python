

class valt_errors:
	def handleerror(self: "VALT", e):
		self.logger.error(__name__ + ": " + str(e))
		if str(e) == "<urlopen error timed out>" or str(e) == "<urlopen error [Errno 11001] getaddrinfo failed>" or str(e) == "HTTP Error 400: Bad Request" or str(e) == "<urlopen error [Errno -3] Temporary failure in name resolution>" or str(e) == "<urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>" or str(e) == "<urlopen error _ssl.c:989: The handshake operation timed out>":
			self.errormsg = "Server Address Unreachable"
			self.accesstoken = 0
			self.reauthenticate(self.failure_reauth_time)
		elif str(e) == "timed out" or str(e) == "Remote end closed connection without response" or str(e) == "The read operation timed out":
			self.errormsg = "Server Did Not Respond"
			self.accesstoken = 0
			self.reauthenticate(self.failure_reauth_time)
		elif str(e) == "HTTP Error 401: Unauthorized":
			self.errormsg = "Invalid Username or Password"
			self.accesstoken = 0
			self.reauthenticate(self.failure_reauth_time)
		elif str(e) == "HTTP Error 404: Not Found":
			if self.accesstoken != 0:
				self.errormsg = "Invalid Room, User, or Recording ID"
			else:
				self.errormsg = "Unable to Connect to VALT Server"
				self.reauthenticate(self.failure_reauth_time)
		elif str(e) == "HTTP Error 502: Bad Gateway":
			self.errormsg = "VALT Server Offline"
			self.accesstoken = 0
			self.reauthenticate(self.failure_reauth_time)
		elif str(e) == "No Recording":
			self.errormsg = "Room is Not Currently Recording"
		elif str(e) == "Room Already Recording":
			self.errormsg = "Unable to Start Recording in a Room that is Already Recording"
		elif str(e) == "Room Paused":
			self.errormsg = "Room is Currently Paused"
		elif str(e) == "Room Not Paused":
			self.errormsg = "Room is Not Currently Paused"
		elif str(e) == "No Cameras":
			self.errormsg = "No Cameras in Room"
		elif str(e) == "No Rooms":
			self.errormsg = "No Rooms Currently Set Up"
		elif str(e) == "No Schedules":
			self.errormsg = "No Schedules Currently Set Up"
		elif str(e) == "Unknown Status":
			self.errormsg = "Room Status Unknown"
		elif str(e) == "No Users":
			self.errormsg = "No Users Currently Set Up"
		elif str(e) == "Not Locked":
			self.errormsg = "Room Not Currently Locked"
		elif str(e) == "No Lock":
			self.errormsg = "Room Cannot Be Locked"
		elif str(e) == "Invalid Room ID":
			self.errormsg = "Invalid Room ID"
		elif str(e) == "Unable to apply preset":
			pass
		elif str(e) == "Unable to get camera presets":
			pass
		elif str(e) == "File not found.":
			pass
		elif str(e) == "Recording Not Found":
			pass
		elif str(e) == "Video Not Found":
			pass
		else:
			self.errormsg = "An Unknown Error Occurred"
			self.accesstoken = 0
			self.reauthenticate(self.failure_reauth_time)
	@property
	def errormsg(self: "VALT"):
		return self._errormsg
	@errormsg.setter
	def errormsg(self: "VALT",newmsg):
		self._errormsg = newmsg
		for callback in self._errormsg_observers:
			callback(self._errormsg)
	def bind_to_errormsg(self: "VALT",callback):
		self._errormsg_observers.append(callback)
	def bind_to_errormg(self: "VALT", callback):
		self.bind_to_errormsg(callback)

