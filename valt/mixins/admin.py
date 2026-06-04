from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtAdmin:
	def setsharing(self: VALT, recid, **kwargs):
		# Function changes sets sharing permission on the specified recording.
		# Users and groups must be passed as lists, enclosed in [].
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
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
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def getrecords(self: VALT, **kwargs):
		# Function to return a list of records.
		# Returns 0 on failure.
		# Each list item is a dictionary with information about the user.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
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
			if isinstance(data, dict) and data['data']:
				return data['data']
			else:
				self.handleerror("No Records")
				return 0

	def getversion(self: VALT):
		# Returns the VALT software version string, or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/general?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if "version" in data['data']:
					return data['data']['version']
				else:
					self.handleerror("No Version")
					return 0
			else:
				return 0

	def get_all_cameras(self: VALT):
		# Function to return a list of all cameras.
		# Returns a list of cameras if successful. Each list item is actually a dictionary containing information about that camera.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/cameras?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
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
			return 0
		else:
			url = self.baseurl + 'rooms/info?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict) and data['data']['rooms']:
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
			return 0
		else:
			if room is not None and room != "" and room != "None":
				url = self.baseurl + 'schedule?access_token=' + self.accesstoken
				roomsched = []
				data = self.send_to_valt(url)
				if isinstance(data, dict) and data['data']['schedules']:
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
		# Function to return the name of the specified user.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/users/' + str(user) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				return data['data']['name']
			else:
				return 0

	def create_camera(self: VALT,camera_name,camera_ip,camera_username,camera_password,**kwargs):
		# Function to start recording in the specified room.
		# Returns camera id on success and 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			values={}
			values['name'] = camera_name
			values['ip'] = camera_ip
			values['device_type'] = "camera"
			values['http_port'] = kwargs.get("camera_http",80)
			values['rtsp_port'] = kwargs.get("camera_rtsp",554)
			values['username'] = camera_username
			values['password'] = camera_password
			values['brand'] = 1
			values['model'] = 1
			values['rooms'] = kwargs.get("rooms",[])
			values['wowza'] = kwargs.get("wowza",1)
			url = self.baseurl + 'admin/cameras?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def create_room(self: VALT,room_name,**kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			values={}
			values['name'] = room_name
			values['wowza'] = kwargs.get("wowza",1)
			url = self.baseurl + 'admin/rooms?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def get_admin_rooms(self: VALT):
		# Returns list of all rooms with full camera details or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get admin rooms")
			return 0

	def get_admin_room(self: VALT, room_id):
		# Returns a room dict with full camera details or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms/{room_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get admin room")
			return 0

	def update_room(self: VALT, room_id, **kwargs):
		# Updates a room. Returns room id or 0 on failure.
		# Optional kwargs: name, is_io, io_camera_id, io_user_id
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms/{room_id}/edit?access_token={self.accesstoken}'
		values = {k: v for k, v in kwargs.items()}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated room {room_id}")
			return data['data'].get('id', 0)
		else:
			self.handleerror("Unable to update room")
			return 0

	def delete_room(self: VALT, room_id):
		# Deletes a room. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms/{room_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted room {room_id}")
			return 1
		else:
			self.handleerror("Unable to delete room")
			return 0

	def get_camera(self: VALT, camera_id):
		# Returns full camera dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/{camera_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get camera")
			return 0

	def update_camera(self: VALT, camera_id, **kwargs):
		# Updates a camera. Returns camera id or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/{camera_id}/edit?access_token={self.accesstoken}'
		values = {k: v for k, v in kwargs.items()}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated camera {camera_id}")
			return data['data'].get('id', 0)
		else:
			self.handleerror("Unable to update camera")
			return 0

	def delete_camera(self: VALT, camera_id):
		# Deletes a camera. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/{camera_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted camera {camera_id}")
			return 1
		else:
			self.handleerror("Unable to delete camera")
			return 0

	def get_camera_brands(self: VALT):
		# Returns list of camera brands and models or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/brands?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('brands', data['data'])
		else:
			self.handleerror("Unable to get camera brands")
			return 0

	def get_media_server(self: VALT, server_id):
		# Returns a media server dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/wowza/{server_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get media server")
			return 0

	def create_media_server(self: VALT, name, address, storage_folder, **kwargs):
		# Creates a media server. Returns new server id or 0 on failure.
		# Optional kwargs: port, ssl
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/wowza?access_token={self.accesstoken}'
		values = {'name': name, 'address': address, 'storage_folder': storage_folder}
		for key in ('port', 'ssl'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created media server '{name}'")
			return data['data'].get('id', 0)
		else:
			self.handleerror("Unable to create media server")
			return 0

	def update_media_server(self: VALT, server_id, **kwargs):
		# Updates a media server. Returns server id or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/wowza/{server_id}/edit?access_token={self.accesstoken}'
		values = {k: v for k, v in kwargs.items()}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated media server {server_id}")
			return data['data'].get('id', 0)
		else:
			self.handleerror("Unable to update media server")
			return 0

	def delete_media_server(self: VALT, server_id):
		# Deletes a media server. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/wowza/{server_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted media server {server_id}")
			return 1
		else:
			self.handleerror("Unable to delete media server")
			return 0

	def get_log_categories(self: VALT):
		# Returns list of log category names or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/logs?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('logs_list', data['data'])
		else:
			self.handleerror("Unable to get log categories")
			return 0

	def get_media_servers(self: VALT):
		# Function to return a list of all cameras.
		# Returns a list of cameras if successful. Each list item is actually a dictionary containing information about that camera.
		# Returns 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/wowza?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if data['data']['media_servers']:
					return data['data']['media_servers']
				else:
					self.handleerror("No Media Servers")
					return 0
			else:
				self.handleerror("No Media Servers")
				return 0
