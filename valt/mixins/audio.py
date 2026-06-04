from __future__ import annotations
from typing import TYPE_CHECKING

import json
import os
import ssl
import uuid
from urllib import request, error

if TYPE_CHECKING:
	from ..valt import VALT

class ValtAudio:
	def get_audio(self: VALT, audio_id):
		# Returns the Audio dict on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'audio/{audio_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict):
			return data
		else:
			self.handleerror("Unable to get audio")
			return 0

	def upload_audio(self: VALT, file_path, duration, frequencies):
		# Uploads a new audio file. Returns the Audio dict on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'audio?access_token={self.accesstoken}'
		data = self._send_audio(url, file_path, duration, frequencies)
		if isinstance(data, dict) and 'id' in data:
			self.logger.info(__name__ + f": Uploaded audio {data['id']}")
			return data
		else:
			self.handleerror("Unable to upload audio")
			return 0

	def update_audio(self: VALT, audio_id, file_path, duration, frequencies):
		# Updates an existing audio file. Returns the Audio dict on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'audio/update/{audio_id}?access_token={self.accesstoken}'
		data = self._send_audio(url, file_path, duration, frequencies)
		if isinstance(data, dict) and 'id' in data:
			self.logger.info(__name__ + f": Updated audio {audio_id}")
			return data
		else:
			self.handleerror("Unable to update audio")
			return 0

	def delete_audio(self: VALT, audio_id):
		# Deletes an audio file. Returns the audio ID on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'audio/{audio_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url, method='DELETE')
		if isinstance(data, dict) and 'id' in data:
			self.logger.info(__name__ + f": Deleted audio {audio_id}")
			return data['id']
		else:
			self.handleerror("Unable to delete audio")
			return 0

	def _send_audio(self: VALT, url, file_path, duration, frequencies):
		# Builds a multipart/form-data request with audioNote, duration, and frequencies.
		if not os.path.isfile(file_path):
			self.handleerror("File not found.")
			return 0

		boundary = uuid.uuid4().hex
		with open(file_path, 'rb') as f:
			file_content = f.read()

		def field(name, value):
			return (
				f'--{boundary}\r\n'
				f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
				f'{value}\r\n'
			).encode()

		body = (
			f'--{boundary}\r\n'
			f'Content-Disposition: form-data; name="audioNote"; filename="{os.path.basename(file_path)}"\r\n'
			f'Content-Type: application/octet-stream\r\n\r\n'
		).encode() + file_content + b'\r\n'
		body += field('duration', str(duration))
		for freq in frequencies:
			body += field('frequencies[]', str(freq))
		body += f'--{boundary}--\r\n'.encode()

		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE

		req = request.Request(url, data=body, method='POST')
		req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
		try:
			response = request.urlopen(req, timeout=self.httptimeout, context=ctx)
			return json.load(response)
		except error.HTTPError as e:
			self.logger.error(__name__ + ": VALT API Call Failed")
			self.handleerror(e)
			return 0
		except Exception as e:
			self.logger.error(__name__ + ": VALT API Call Failed")
			self.handleerror(e)
			return 0
