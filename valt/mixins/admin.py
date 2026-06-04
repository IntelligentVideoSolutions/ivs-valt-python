from __future__ import annotations
from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
	from ..valt import VALT

class ValtAdmin:
	def set_sharing(self: VALT, recid, **kwargs):
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
				self.handle_error("No Users or Groups Specified")
				return 0
			url = self.baseurl + 'records/' + str(recid) + '/update?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			self.logger.info(__name__ + ": " + "Sharing Permissions Updated")
			self.logger.debug(__name__ + ": " + str(values))
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def get_records(self: VALT, **kwargs):
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
				self.handle_error("No Search Criteria Specified")
				return 0
			url = self.baseurl + 'records?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict) and data['data']:
				return data['data']
			else:
				self.handle_error("No Records")
				return 0

	def get_version(self: VALT):
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
					self.handle_error("No Version")
					return 0
			else:
				return 0

	def get_all_cameras(self: VALT):
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
					self.handle_error("No Cameras")
					return 0
			else:
				self.handle_error("No Cameras")
				return 0

	def get_rooms(self: VALT):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/info?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict) and data['data']['rooms']:
				return data['data']['rooms']
			else:
				self.handle_error("No Rooms")
				return 0

	def get_room_schedule(self: VALT, room):
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
						self.handle_error("No Schedules")
						return 0
				else:
					self.handle_error("No Schedules")
					return 0
			else:
				self.handle_error("Invalid Room ID")
				return 0

	def get_username(self: VALT, user):
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

	def create_camera(self: VALT, camera_name, camera_ip, camera_username, camera_password, **kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			values = {}
			values['name'] = camera_name
			values['ip'] = camera_ip
			values['device_type'] = "camera"
			values['http_port'] = kwargs.get("camera_http", 80)
			values['rtsp_port'] = kwargs.get("camera_rtsp", 554)
			values['username'] = camera_username
			values['password'] = camera_password
			values['brand'] = 1
			values['model'] = 1
			values['rooms'] = kwargs.get("rooms", [])
			values['wowza'] = kwargs.get("wowza", 1)
			url = self.baseurl + 'admin/cameras?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def create_room(self: VALT, room_name, **kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			values = {}
			values['name'] = room_name
			values['wowza'] = kwargs.get("wowza", 1)
			url = self.baseurl + 'admin/rooms?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def get_admin_rooms(self: VALT):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get admin rooms")
			return 0

	def get_admin_room(self: VALT, room_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms/{room_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get admin room")
			return 0

	def update_room(self: VALT, room_id, **kwargs):
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
			self.handle_error("Unable to update room")
			return 0

	def delete_room(self: VALT, room_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/rooms/{room_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted room {room_id}")
			return 1
		else:
			self.handle_error("Unable to delete room")
			return 0

	def get_camera(self: VALT, camera_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/{camera_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get camera")
			return 0

	def update_camera(self: VALT, camera_id, **kwargs):
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
			self.handle_error("Unable to update camera")
			return 0

	def delete_camera(self: VALT, camera_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/{camera_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted camera {camera_id}")
			return 1
		else:
			self.handle_error("Unable to delete camera")
			return 0

	def get_camera_brands(self: VALT):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/cameras/brands?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('brands', data['data'])
		else:
			self.handle_error("Unable to get camera brands")
			return 0

	def get_media_server(self: VALT, server_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/wowza/{server_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get media server")
			return 0

	def create_media_server(self: VALT, name, address, storage_folder, **kwargs):
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
			self.handle_error("Unable to create media server")
			return 0

	def update_media_server(self: VALT, server_id, **kwargs):
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
			self.handle_error("Unable to update media server")
			return 0

	def delete_media_server(self: VALT, server_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/wowza/{server_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted media server {server_id}")
			return 1
		else:
			self.handle_error("Unable to delete media server")
			return 0

	def get_log_categories(self: VALT):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/logs?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('logs_list', data['data'])
		else:
			self.handle_error("Unable to get log categories")
			return 0

	def get_media_servers(self: VALT):
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
					self.handle_error("No Media Servers")
					return 0
			else:
				self.handle_error("No Media Servers")
				return 0

	# ── Deprecated aliases ────────────────────────────────────────

	def setsharing(self: VALT, recid, **kwargs):
		warnings.warn("setsharing is deprecated and will be removed in a future version. Use set_sharing instead.", DeprecationWarning, stacklevel=2)
		return self.set_sharing(recid, **kwargs)

	def getrecords(self: VALT, **kwargs):
		warnings.warn("getrecords is deprecated and will be removed in a future version. Use get_records instead.", DeprecationWarning, stacklevel=2)
		return self.get_records(**kwargs)

	def getversion(self: VALT):
		warnings.warn("getversion is deprecated and will be removed in a future version. Use get_version instead.", DeprecationWarning, stacklevel=2)
		return self.get_version()

	def getrooms(self: VALT):
		warnings.warn("getrooms is deprecated and will be removed in a future version. Use get_rooms instead.", DeprecationWarning, stacklevel=2)
		return self.get_rooms()

	def getschedule(self: VALT, room):
		warnings.warn("getschedule is deprecated and will be removed in a future version. Use get_room_schedule instead.", DeprecationWarning, stacklevel=2)
		return self.get_room_schedule(room)

	def getusername(self: VALT, user):
		warnings.warn("getusername is deprecated and will be removed in a future version. Use get_username instead.", DeprecationWarning, stacklevel=2)
		return self.get_username(user)
