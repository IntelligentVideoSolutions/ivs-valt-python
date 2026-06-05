from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtRights:
	def get_rights(self: VALT):
		# Returns list of all rights or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'rights?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get rights")
			return 0

	def get_rights_by_type(self: VALT, right_type):
		# Returns rights object for the given type or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'rights/{right_type}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get rights")
			return 0
