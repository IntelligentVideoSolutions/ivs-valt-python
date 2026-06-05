from __future__ import annotations
from typing import TYPE_CHECKING

import ssl
import urllib.request

if TYPE_CHECKING:
	from ..valt import VALT

class ValtDownload:
	def download_video(self: VALT, recording_id, video_id, file_name):
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'records/download/{recording_id}/{video_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict):
			if data['url']:
				ctx = ssl.create_default_context()
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
				try:
					with urllib.request.urlopen(data['url'], timeout=self.httptimeout, context=ctx) as response:
						with open(file_name, "wb") as f:
							f.write(response.read())
					self.logger.info(f"{__name__}: File saved successfully as {file_name}")
					return 1
				except Exception as e:
					self.logger.error(f"{__name__}: Failed to download: {e}")
					return 0
			else:
				self.handle_error("Video Not Found")
				return 0
		else:
			self.handle_error("Video Not Found")
			return 0
