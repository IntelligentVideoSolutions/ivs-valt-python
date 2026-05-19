from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class valt_admin:
	def setsharing(self: VALT, recid, **kwargs):
		# Function changes sets sharing permission on the specified recording.
		# Users and groups must be passed as lists, enclosed in [].
		# Returns 0 on failure.
		# Returns 99 if not currently authenticated to VALT
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			if 'users' in kwargs and 'groups' in kwargs:
				values = {"share": {"users": kwargs['users'], "groups": kwargs['groups']}}
			elif 'users' in kwargs:
				values = {"share": {"users": kwargs['users']}}
			elif 'groups' in kwargs:
				values = {"share": {"groups": kwargs['groups']}}
			else:
				self.handleerror("No Users or Groups Specified")
				return 0
			url = self.baseurl + 'records/' + str(recid) + '/update?access_token=' + self.accesstoken
			data = self.send_to_valt(url,values=values)
			self.logger.info(__name__ + ": " + "Sharing Permissions Updated")
			self.logger.debug(__name__ + ": " + str(values))
			if type(data).__name__ == "dict":
				return data['data']['id']

	def getrecords(self: VALT, **kwargs):
		# Function to return a list of records.
		# Returns 0 on failure.
		# Each list item is a dictionary with information about the user.
		# Returns 99 if not currently authenticated to VALT
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			if 'search' in kwargs and 'start_date' in kwargs:
				values = {"search": kwargs['search'], "start_date": kwargs['start_date']}
			elif 'search' in kwargs:
				values = {"search": kwargs['search']}
			elif 'start_date' in kwargs:
				values = {"start_date": kwargs['start_date']}
			else:
				self.handleerror("No Search Criteria Specified")
				return 0
			url = self.baseurl + 'records?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if data['data']:
				return data['data']
			else:
				self.handleerror("No Records")
				return 0
	def getversion(self: VALT):
		# Function to get the current active recording id in the specified room
		# Returns true if the specified room is recording
		# Returns False if the room is not recording
		# Returns 2 if an error is encountered
		# Returns 99 if not currently authenticated to VALT
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'admin/general?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if "version" in data['data'].keys():
					return data['data']['version']
				else:
					self.handleerror("No Version")
					return 0
	def get_all_cameras(self: VALT):
		# Function to return a list of all cameras.
		# Returns a list of cameras if successful. Each list item is actually a dictionary containing information about that camera.
		# Returns 0 on failure.
		# Returns 99 if not currently authenticated to VALT
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'admin/cameras?access_token=' + self.accesstoken
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

	def getrooms(self: VALT):
		# Function to return a list of all rooms.
		# Returns a list of rooms if successful. Each list item is actually a dictionary containing information about that room.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'rooms/info?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if data['data']['rooms']:
				return data['data']['rooms']
			else:
				self.handleerror("No Rooms")
				return 0

	def getschedule(self: VALT, room):
		# Function to return a list of scheduled recordings for the specified room.
		# Returns a list of schedules if successful. Each list item is actually a list containing information about that schedule.
		# Returns 0 on failure.
		# Returns an empty list if no schedules exist for the specified room.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			if room != None and room != "" and room != "None":
				url = self.baseurl + 'schedule?access_token=' + self.accesstoken
				roomsched = []
				data = self.send_to_valt(url)
				if data['data']['schedules']:
					for schedule in data['data']['schedules']:
						for rooms in schedule['rooms']:
							if rooms['id'] == int(room):
								templist = []
								templist.append(schedule['start_at'])
								templist.append(schedule['stop_at'])
								templist.append(schedule['name'])
								roomsched.append(templist)
					roomsched.sort()
					if roomsched:
						if self.errormsg == "No Schedules Currently Set Up":
							self.errormsg = None
						return roomsched
					else:
						self.handleerror("No Schedules")
						return 0
				else:
					self.handleerror("No Schedules")
					return 0
			else:
				self.handleerror("Invalid Room ID")
				return 0

	def getusername(self: VALT, user):
		# Function to return the name of the specified room.
		# Returns 99 if not currently authenticated to VALT
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'admin/users/' + str(user) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				return data['data']['name']

	def create_camera(self: VALT,camera_name,camera_ip,camera_username,camera_password,**kwargs):
		# Function to start recording in the specified room.
		# Returns camera id on success and 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			values={}
			values['name'] = camera_name
			values['ip'] = camera_ip
			values['device_type'] = "camera"
			values['http_port'] = kwargs.get("camera_http",80)
			values['rtsp_port'] = kwargs.get("camera_http",554)
			values['username'] = camera_username
			values['password'] = camera_password
			values['brand'] = 1
			values['model'] = 1
			values['rooms'] = kwargs.get("rooms",[])
			values['wowza'] = kwargs.get("wowza",1)
			url = self.baseurl + 'admin/cameras?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if type(data).__name__ == "dict":
				return data['data']['id']
			else:
				return 0
	def create_room(self: VALT,room_name,**kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			values={}
			values['name'] = room_name
			values['wowza'] = kwargs.get("wowza",1)
			url = self.baseurl + 'admin/rooms?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if type(data).__name__ == "dict":
				return data['data']['id']
			else:
				return 0

	def get_media_servers(self: VALT):
		# Function to return a list of all cameras.
		# Returns a list of cameras if successful. Each list item is actually a dictionary containing information about that camera.
		# Returns 0 on failure.
		# Returns 99 if not currently authenticated to VALT
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'admin/wowza?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['data']['media_servers']:
					return data['data']['media_servers']
				else:
					self.handleerror("No Media Servers")
					return 0
			else:
				self.handleerror("No Media Servers")
				return 0
