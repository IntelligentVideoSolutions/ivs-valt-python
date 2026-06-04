from __future__ import annotations
from typing import TYPE_CHECKING

import os
import ssl
import urllib.request

if TYPE_CHECKING:
	from ..valt import VALT

class valt_recording:
	def upload_video(self: VALT,file_path,upload_name):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		if os.path.isfile(file_path):
			url = f"{self.baseurl}records/create-upload?access_token={self.accesstoken}"
			values = {"name": upload_name}
			data = self.send_to_valt(url,values=values)
			if isinstance(data, dict):
				record_id = data['id']
				videos = data['videos'][0]
				url = f"{self.baseurl}records/{record_id}/videos/{videos}?access_token={self.accesstoken}"
				result = self.send_to_valt(url,file_path=file_path)
				if result is None:
					self.logger.warning(__name__ + ": Upload may have failed or returned no response")
					return 0
				return record_id
			else:
				self.handleerror("Upload Creation Failed.")
				return 0
		else:
			self.handleerror("File not found.")
			return 0
	def download_video(self: VALT,recording_id,video_id,file_name):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
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
					self.handleerror("Video Not Found")
					return 0
			else:
				self.handleerror("Video Not Found")
				return 0
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
