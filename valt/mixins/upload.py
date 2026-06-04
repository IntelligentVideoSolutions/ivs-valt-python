from __future__ import annotations
from typing import TYPE_CHECKING

import os

if TYPE_CHECKING:
	from ..valt import VALT

class ValtUpload:
	def upload_video(self: VALT, file_path, upload_name):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		if os.path.isfile(file_path):
			url = f"{self.baseurl}records/create-upload?access_token={self.accesstoken}"
			values = {"name": upload_name}
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict) and 'id' in data and data.get('videos'):
				record_id = data['id']
				videos = data['videos'][0]
				url = f"{self.baseurl}records/{record_id}/videos/{videos}?access_token={self.accesstoken}"
				self.send_to_valt(url, file_path=file_path)
				if self.accesstoken != 0:
					return record_id
				return 0
			else:
				self.handleerror("Upload Creation Failed.")
				return 0
		else:
			self.handleerror("File not found.")
			return 0
