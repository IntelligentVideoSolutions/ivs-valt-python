from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtRecording:
	def get_video_information(self: VALT,recording_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + f'records/{recording_id}?access_token={self.accesstoken}'
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if data['data'] is not None:
					return data['data']
				else:
					self.handleerror("Recording Not Found")
					return 0
			else:
				self.handleerror("Recording Not Found")
				return 0
