from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class valt_groups:
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
