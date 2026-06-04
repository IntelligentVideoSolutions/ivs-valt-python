from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtSchedule:
	def get_blocked_schedules(self: VALT):
		# Returns list of blocked schedules or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/blocked?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('blocked_schedules', data['data'])
		else:
			self.handleerror("Unable to get blocked schedules")
			return 0

	def get_conflict_schedules(self: VALT):
		# Returns list of conflict schedules or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/conflict?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('conflict_schedules', data['data'])
		else:
			self.handleerror("Unable to get conflict schedules")
			return 0

	def get_schedule(self: VALT, schedule_id):
		# Returns a schedule dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/{schedule_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get schedule")
			return 0

	def create_schedule(self: VALT, name, room, start_at, duration, **kwargs):
		# Creates a schedule. Returns new schedule id or 0 on failure.
		# Optional kwargs: template, recurrence, share
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule?access_token={self.accesstoken}'
		values = {'name': name, 'room': room, 'start_at': start_at, 'duration': duration}
		for key in ('template', 'recurrence', 'share'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, list) and len(data) > 0:
			self.logger.info(__name__ + f": Created schedule '{name}'")
			return data[0]
		elif isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created schedule '{name}'")
			return data['data']
		else:
			self.handleerror("Unable to create schedule")
			return 0

	def update_schedule(self: VALT, schedule_id, **kwargs):
		# Updates a schedule. Returns 1 on success or 0 on failure.
		# Optional kwargs: name, room, start_at, duration, template, recurrence, share
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/{schedule_id}/edit?access_token={self.accesstoken}'
		values = {k: v for k, v in kwargs.items()}
		self.send_to_valt(url, values=values)
		if self.accesstoken != 0:
			self.logger.info(__name__ + f": Updated schedule {schedule_id}")
			return 1
		return 0

	def delete_next_schedule(self: VALT, schedule_id):
		# Deletes the next occurrence of a recurring schedule.
		# Returns the updated schedule dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/{schedule_id}/delete_next?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted next occurrence of schedule {schedule_id}")
			return data['data']
		else:
			self.handleerror("Unable to delete next schedule")
			return 0

	def stop_schedule(self: VALT, schedule_id):
		# Stops a running schedule. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/{schedule_id}/stop?access_token={self.accesstoken}'
		self.send_to_valt(url, values={})
		if self.accesstoken != 0:
			self.logger.info(__name__ + f": Stopped schedule {schedule_id}")
			return 1
		return 0

	def delete_schedule(self: VALT, schedule_id):
		# Deletes a schedule. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'schedule/{schedule_id}/delete?access_token={self.accesstoken}'
		self.send_to_valt(url, values={})
		if self.accesstoken != 0:
			self.logger.info(__name__ + f": Deleted schedule {schedule_id}")
			return 1
		return 0
