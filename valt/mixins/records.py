from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtRecords:
	def cut_record(self: VALT, record_id, start_time, end_time):
		# Cuts a record between start_time and end_time (seconds).
		# Returns dict with clip_id and message on success, or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'records/{record_id}/cut?access_token={self.accesstoken}'
		values = {'start_time': start_time, 'end_time': end_time}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Cut started on record {record_id}")
			return data['data']
		else:
			self.handle_error("Unable to cut record")
			return 0

	def get_cut_status(self: VALT, clip_id):
		# Returns True if cut is complete, False if still processing, or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'records/{clip_id}/cut/status?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('status', False)
		else:
			self.handle_error("Unable to get cut status")
			return 0

	def delete_record(self: VALT, record_id):
		# Deletes a record. Returns 1 on success or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'records/{record_id}/delete?access_token={self.accesstoken}'
		self.send_to_valt(url, values={})
		if self.accesstoken != 0:
			self.logger.info(__name__ + f": Deleted record {record_id}")
			return 1
		return 0

	def share_record(self: VALT, record_id):
		# Generates a share URL for a record. Returns the URL string or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'records/{record_id}/share?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('url', 0)
		else:
			self.handle_error("Unable to share record")
			return 0

	def deactivate_share(self: VALT, record_id):
		# Removes the share URL for a record. Returns 1 on success or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'records/{record_id}/share/deactivate?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Share deactivated for record {record_id}")
			return 1
		else:
			self.handle_error("Unable to deactivate share")
			return 0
