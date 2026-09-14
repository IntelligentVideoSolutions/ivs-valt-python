from __future__ import annotations
from typing import TYPE_CHECKING

import os
import time

if TYPE_CHECKING:
	from ..valt import VALT

# The HTTP transfer in step 2 of upload_video() is already complete by the time
# send_to_valt() returns, so this isn't waiting on slow bytes - it's tolerating real
# server-side processing time: a freshly uploaded video's status.type is "created"
# until the server finishes processing it into "ready" (confirmed against a live VALT
# 6.7.2 server and https://ivs.help/wiki/index.php/API_Recording_Details). Graduated
# rather than fixed-interval since processing time scales with file size.
_UPLOAD_VERIFY_DELAYS_SECONDS = (3, 5, 10, 15, 15)

class ValtUpload:
	def upload_video(self: VALT, file_path, upload_name):
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		if os.path.isfile(file_path):
			url = f"{self.baseurl}records/create-upload?access_token={self.accesstoken}"
			values = {"name": upload_name}
			data = self.send_to_valt(url, values=values)
			if isinstance(data, dict) and 'id' in data and data.get('videos'):
				record_id = data['id']
				video_id = data['videos'][0]
				url = f"{self.baseurl}records/{record_id}/videos/{video_id}?access_token={self.accesstoken}"
				# send_to_valt() returns None on any transport/HTTP failure, or on the
				# 2xx-with-empty-body response this endpoint always returns on success
				# (confirmed via record_upload.md) - neither is distinguishable from
				# "actually succeeded" using this return value alone, so it is captured
				# here for logging/future-proofing only. Success/failure is decided
				# below by independently re-querying the record.
				upload_response = self.send_to_valt(url, file_path=file_path)
				self.logger.debug(__name__ + f": upload response for video {video_id}: {upload_response!r}")
				if self._video_uploaded(record_id, video_id):
					return record_id
				self.handle_error("Upload Verification Failed")
				return 0
			else:
				self.handle_error("Upload Creation Failed.")
				return 0
		else:
			self.handle_error("File not found.")
			return 0

	def _video_uploaded(self: VALT, record_id, video_id) -> bool:
		# records/create-upload (step 1) pre-allocates the video_id slot before any file
		# bytes are sent, so video_id appearing in records/{id} is not by itself proof
		# the file content landed - status.type must reach "ready" specifically.
		attempts = len(_UPLOAD_VERIFY_DELAYS_SECONDS) + 1
		for attempt in range(1, attempts + 1):
			try:
				info = self.get_video_information(record_id)
			except Exception as e:
				# get_video_information() does `data['data']` without .get() - guard
				# against an unexpected response shape crashing the upload thread.
				self.logger.debug(__name__ + f": get_video_information({record_id}) raised {e!r} on attempt {attempt}")
				info = 0
			if isinstance(info, dict):
				# A record whose file was never actually uploaded has `videos: null`
				# here (confirmed live), not a missing key or an empty list - `.get(...,
				# [])` alone would still crash on that, hence `or []`.
				video = next((v for v in (info.get('videos') or []) if v.get('id') == video_id), None)
				if video is not None:
					status_type = (video.get('status') or {}).get('type')
					self.logger.debug(__name__ + f": video {video_id} status.type={status_type!r} on attempt {attempt}")
					if status_type == 'ready':
						return True
					# "created" (still processing) or any unrecognized value - keep retrying.
				else:
					self.logger.debug(__name__ + f": video {video_id} not yet present on attempt {attempt}")
			else:
				self.logger.debug(__name__ + f": get_video_information({record_id}) returned {info!r} on attempt {attempt}")
				if not self.connected:
					break  # further attempts can't succeed - stop early
			if attempt <= len(_UPLOAD_VERIFY_DELAYS_SECONDS):
				time.sleep(_UPLOAD_VERIFY_DELAYS_SECONDS[attempt - 1])
		return False
