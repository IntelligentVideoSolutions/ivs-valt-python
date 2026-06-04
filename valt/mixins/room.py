from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class valt_room:
	def isrecording(self: VALT, room):
		# Function to check if the specified room is currently recording
		# Returns true if the specified room is recording
		# Returns False if the room is not recording
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				return data['data']['has_recording']
			else:
				return 0


	def getrecordingid(self: VALT, room):
		# Function to get the current active recording id in the specified room
		# Returns recording id if currently recording
		# Returns 0 if the room is not recording
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if "recording" in data['data'].keys():
					return data['data']['recording']['id']
				else:
					self.handleerror("No Recording")
					return 0
			else:
				return 0


	def startrecording(self: VALT, room, name, **kwargs):
		# Function to start recording in the specified room.
		# Returns recording id on success and 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.isrecording(room)
			if is_recording is True:
				self.handleerror("Room Already Recording")
				return 0
			if is_recording is not False:
				return 0
			if 'author' in kwargs:
				values = {"name": name, "author": kwargs['author']}
			else:
				values = {"name": name}

			url = self.baseurl + 'rooms/' + str(room) + '/record/start' + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if 'author' in kwargs:
				self.logger.info(__name__ + ": " + "Recording " + name + " started in " + str(self.getroomname(room)) + " by " + str(self.getusername(kwargs['author'])))
			else:
				self.logger.info(__name__ + ": " + "Recording " + name + " started in " + str(self.getroomname(room)))
			if room == self.selected_room:
				self.selected_room_status = 2
			if type(data).__name__ == "dict":
				return data['data']['id']
			else:
				return 0


	def stoprecording(self: VALT, room):
		# Function to stop recording in the specified room.
		# Returns recording id on success and 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.isrecording(room)
			if is_recording is True:
				url = self.baseurl + 'rooms/' + str(room) + '/record/stop' + '?access_token=' + self.accesstoken
				values = {"nothing": "nothing"}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Recording stopped in " + str(self.getroomname(room)))
				if room == self.selected_room:
					self.selected_room_status = 1
				if type(data).__name__ == "dict":
					return data['data']['id']
				else:
					return 0
			elif is_recording is False:
				self.handleerror("No Recording")
				return 0
			else:
				return 0


	def pauserecording(self: VALT, room):
		# Function to pause recording in the specified room.
		# Returns recording id on success and 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.isrecording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handleerror("No Recording")
				return 0
			paused = self.ispaused(room)
			if paused is False:
				url = self.baseurl + 'rooms/' + str(room) + '/record/pause' + '?access_token=' + self.accesstoken
				values = {"nothing": "nothing"}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Recording paused in " + str(self.getroomname(room)))
				if room == self.selected_room:
					self.selected_room_status = 3
				if type(data).__name__ == "dict":
					return data['data']['id']
				else:
					return 0
			elif paused is True:
				self.handleerror("Room Paused")
				return 0
			else:
				return 0


	def resumerecording(self: VALT, room):
		# Function to resume recording in the specified room.
		# Returns recording id on success and 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.isrecording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handleerror("No Recording")
				return 0
			paused = self.ispaused(room)
			if paused is True:
				url = self.baseurl + 'rooms/' + str(room) + '/record/resume' + '?access_token=' + self.accesstoken
				values = {"nothing": "nothing"}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Recording resumed in " + str(self.getroomname(room)))
				if room == self.selected_room:
					self.selected_room_status = 2
				if type(data).__name__ == "dict":
					return data['data']['id']
				else:
					return 0
			elif paused is False:
				self.handleerror("Room Not Paused")
				return 0
			else:
				return 0


	def addcomment(self: VALT, room, markername, color="red", **kwargs):
		# Function to add a comment current recording in specified room.
		# Returns 1 if successful.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.isrecording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handleerror("No Recording")
				return 0
			if self.version[0] == "6":
					url = self.baseurl + 'comment?access_token=' + self.accesstoken
				elif self.version[0] == "5":
					url = self.baseurl + 'rooms/' + str(room) + '/record/markers' + '?access_token=' + self.accesstoken
				else:
					self.logger.error(__name__ + ": Unable to Determine VALT version")
					return 0
				markertime = self.getrecordingtime(room)
				if markertime > 0:
					if self.version[0] == "6":
						values = {"recordTime": markertime, "recordId": self.getrecordingid(room), "type": "simple", "message":markername}
					elif self.version[0] == "5":
						values = {"event": markername, "time": markertime, "color": color}
					data = self.send_to_valt(url, values=values)
					self.logger.info(__name__ + ": " + "Comment " + markername + " added in " + str(self.getroomname(room)))
					return 1
				else:
					return 0

	def getrecordingtime(self: VALT, room):
		# Returns current recording time index in seconds for the specified room.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.isrecording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handleerror("No Recording")
				return 0
			url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				return data['data']['recording']['time']
			else:
				return 0

	def ispaused(self: VALT, room):
		# Function to check if specified room is currently recording and paused.
		# Returns true if room is currently paused
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/' + str(room) + '/status?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['data']['status'] == 'paused':
					return True
				else:
					return False
			return False

	def islocked(self: VALT, room):
		# Function to check if specified room is currently locked.
		# Returns true if room is currently locked.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/' + str(room) + '/status?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['data']['status'] == 'locked':
					return True
				else:
					return False
			return False

	def getcameras(self: VALT, room):
		return self.get_cameras(room)

	def get_cameras(self: VALT, room):
		# Function to return a list of all cameras in the specified room.
		# Returns a list of cameras if successful. Each list item is actually a dictionary containing information about that camera.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			if room != None and room != "" and room != "None":
				url = self.baseurl + 'admin/rooms/' + str(room) + '/cameras?access_token=' + self.accesstoken
				data = self.send_to_valt(url)
				if type(data).__name__ == "dict":
					if data['data']['cameras']:
						return data['data']['cameras']
					else:
						self.handleerror("No Cameras")
						return 0
				else:
					self.handleerror("No Cameras")
					return 0
			else:
				self.handleerror("Invalid Room ID")
				return 0

	def getroomname(self: VALT, room):
		# Function to return the name of the specified room.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			if room != None and room != "" and room != "None":
				url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
				data = self.send_to_valt(url)
				if type(data).__name__ == "dict":
					return data['data']['name']
				else:
					return 0
			else:
				return 0

	def getroomstatus(self: VALT, room):
		# Function to return the current state of the specified room.
		# Returns 0 on failure.
		# Returns 1 if the room is available.
		# Returns 2 if the room is recording.
		# Returns 3 if the room is paused.
		# Returns 4 if the room is locked.
		# Returns 5 if the room is prepared.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/' + str(room) + '/status?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['data']['status'] == 'available':
					return 1
				elif data['data']['status'] == 'recording':
					return 2
				elif data['data']['status'] == 'paused':
					return 3
				elif data['data']['status'] == 'locked':
					return 4
				elif data['data']['status'] == 'prepared':
					return 5
				else:
					self.handleerror("Unknown Status")
					return 0
			else:
				self.handleerror("Invalid Room ID")
				return 0

	def lockroom(self: VALT, room):
		# Function locks the specified room.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		room_status = self.getroomstatus(room)
		if room_status == 1 or room_status == 5:
			url = self.baseurl + 'rooms/' + str(room) + '/lock' + '?access_token=' + self.accesstoken
			values = {"nothing": "nothing"}
			data = self.send_to_valt(url, values=values)
			self.logger.info(__name__ + ": " + str(self.getroomname(room)) + " Locked")
			if type(data).__name__ == "dict":
				return data['data']['id']
			else:
				return 0
		else:
			self.handleerror("No Lock")
			return 0

	def unlockroom(self: VALT, room):
		# Function unlocks the specified room.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		if self.islocked(room):
			url = self.baseurl + 'rooms/' + str(room) + '/unlock' + '?access_token=' + self.accesstoken
			values = {"nothing": "nothing"}
			data = self.send_to_valt(url, values=values)
			self.logger.info(__name__ + ": " + str(self.getroomname(room)) + " Unlocked")
			if type(data).__name__ == "dict":
				return data['data']['id']
			else:
				return 0
		else:
			self.handleerror("Not Locked")
			return 0
