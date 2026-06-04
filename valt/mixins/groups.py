from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtGroups:
	def get_user_groups(self: VALT):
		# Returns list of all user groups or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/user_groups?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('userGroups', data['data'])
		else:
			self.handle_error("Unable to get user groups")
			return 0

	def get_user_group_info(self: VALT,group_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/user_groups/' + str(group_id) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				return data['data']
			else:
				return 0
	def get_user_group_rooms(self: VALT,group_id):
		data = self.get_user_group_info(group_id)
		if data != 0:
			if 'rooms' in data:
				return data['rooms']
			else:
				return []
		else:
			return []



	def create_user_group(self: VALT, name, **kwargs):
		# Creates a user group. Returns new group id or 0 on failure.
		# Optional kwargs: template, rights, max_record_duration, rooms, video_access, retention
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/user_groups?access_token={self.accesstoken}'
		values = {'name': name}
		for key in ('template', 'rights', 'max_record_duration', 'rooms', 'video_access', 'retention'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created user group '{name}'")
			return data['data'].get('id', 0)
		else:
			self.handle_error("Unable to create user group")
			return 0

	def delete_user_group(self: VALT, group_id):
		# Deletes a user group. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/user_groups/{group_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted user group {group_id}")
			return 1
		else:
			self.handle_error("Unable to delete user group")
			return 0

	def update_group(self: VALT,group_id,**kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/user_groups/' + str(group_id) + '/edit?access_token=' + self.accesstoken
			values = {}
			if "name" in kwargs:
				values['name'] = kwargs['name']
			if "template" in kwargs:
				values['template'] = kwargs['template']
			if "max_record_duration" in kwargs:
				values['max_record_duration'] = kwargs['max_record_duration']
			if "rooms" in kwargs:
				values['rooms'] = kwargs['rooms']
			if "video_access" in kwargs:
				values['video_access'] = kwargs['video_access']
			if "retention" in kwargs:
				values['retention'] = kwargs['retention']
			if "rights" in kwargs:
				values['rights'] = kwargs['rights']
			data = self.send_to_valt(url,values=values)
			if isinstance(data, dict):
				return data['data']
			else:
				return 0
