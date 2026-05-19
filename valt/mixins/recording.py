from __future__ import annotations
from typing import TYPE_CHECKING

import os
import urllib.request

if TYPE_CHECKING:
	from ..valt import VALT

class valt_recording:
	def upload_video(self: VALT,file_path,upload_name):
		if os.path.isfile(file_path):
			if self.accesstoken == 0:
				self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			else:
				url = f"{self.baseurl}records/create-upload?access_token={self.accesstoken}"
				values = {"name": upload_name}
				data = self.send_to_valt(url,values=values)
				if type(data).__name__ == "dict":
					record_id = data['id']
					videos = data['videos'][0]
					url = f"{self.baseurl}records/{record_id}/videos/{videos}?access_token={self.accesstoken}"
					self.send_to_valt(url,file_path=file_path)
				else:
					self.handleerror("Upload Creation Failed.")
					return 0
		else:
			self.handleerror("File not found.")
			return 0
	def download_video(self: VALT,recording_id,video_id,file_name):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + f'records/download/{recording_id}/{video_id}?access_token={self.accesstoken}'
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['url']:
					try:
						# 1. Open the URL
						with urllib.request.urlopen(data['url']) as response:
							# 2. Read the binary data
							data = response.read()

							# 3. Write to a local file in 'wb' (write binary) mode
							with open(file_name, "wb") as f:
								f.write(data)

						self.logger.info(f"{__name__}: File saved successfully as {file_name}")

					except Exception as e:
						self.logger.error(f"{__name__}: Failed to download: {e}")
				else:
					self.handleerror("Video Not Found")
					return 0
			else:
				self.handleerror("Video Not Found")
				return 0
	def get_video_information(self: VALT,recording_id):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + f'records/{recording_id}?access_token={self.accesstoken}'
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['data']:
					return data['data']
				else:
					self.handleerror("Recording Not Found")
					return 0
			else:
				self.handleerror("Recording Mot Found")
				return 0
