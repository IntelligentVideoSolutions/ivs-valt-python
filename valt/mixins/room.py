from __future__ import annotations
from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
	from ..valt import VALT

class ValtRoom:
	def is_recording(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				return data['data']['has_recording']
			else:
				return 0

	def get_recording_id(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if "recording" in data['data']:
					return data['data']['recording']['id']
				else:
					self.handle_error("No Recording")
					return 0
			else:
				return 0

	def start_recording(self: VALT, room, name, **kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.is_recording(room)
			if is_recording is True:
				self.handle_error("Room Already Recording")
				return 0
			if is_recording is not False:
				return 0
			if 'author' in kwargs:
				values = {"name": name, "author": kwargs['author']}
			else:
				values = {"name": name}

			url = self.baseurl + 'rooms/' + str(room) + '/record/start' + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=values)
			if 'author' in kwargs:
				self.logger.info(__name__ + ": " + "Recording " + name + " started in " + str(self.get_room_name(room)) + " by " + str(self.get_username(kwargs['author'])))
			else:
				self.logger.info(__name__ + ": " + "Recording " + name + " started in " + str(self.get_room_name(room)))
			if room == self.selected_room:
				self.selected_room_status = 2
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0

	def stop_recording(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.is_recording(room)
			if is_recording is True:
				url = self.baseurl + 'rooms/' + str(room) + '/record/stop' + '?access_token=' + self.accesstoken
				values = {"nothing": "nothing"}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Recording stopped in " + str(self.get_room_name(room)))
				if room == self.selected_room:
					self.selected_room_status = 1
				if isinstance(data, dict):
					return data['data']['id']
				else:
					return 0
			elif is_recording is False:
				self.handle_error("No Recording")
				return 0
			else:
				return 0

	def pause_recording(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.is_recording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handle_error("No Recording")
				return 0
			paused = self.is_paused(room)
			if paused is False:
				url = self.baseurl + 'rooms/' + str(room) + '/record/pause' + '?access_token=' + self.accesstoken
				values = {"nothing": "nothing"}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Recording paused in " + str(self.get_room_name(room)))
				if room == self.selected_room:
					self.selected_room_status = 3
				if isinstance(data, dict):
					return data['data']['id']
				else:
					return 0
			elif paused is True:
				self.handle_error("Room Paused")
				return 0
			else:
				return 0

	def resume_recording(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.is_recording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handle_error("No Recording")
				return 0
			paused = self.is_paused(room)
			if paused is True:
				url = self.baseurl + 'rooms/' + str(room) + '/record/resume' + '?access_token=' + self.accesstoken
				values = {"nothing": "nothing"}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Recording resumed in " + str(self.get_room_name(room)))
				if room == self.selected_room:
					self.selected_room_status = 2
				if isinstance(data, dict):
					return data['data']['id']
				else:
					return 0
			elif paused is False:
				self.handle_error("Room Not Paused")
				return 0
			else:
				return 0

	def add_comment(self: VALT, room, markername, color="red", **kwargs):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.is_recording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handle_error("No Recording")
				return 0
			if self.version[0] == "6":
				url = self.baseurl + 'comment?access_token=' + self.accesstoken
			elif self.version[0] == "5":
				url = self.baseurl + 'rooms/' + str(room) + '/record/markers' + '?access_token=' + self.accesstoken
			else:
				self.logger.error(__name__ + ": Unable to Determine VALT version")
				return 0
			markertime = self.get_recording_time(room)
			if markertime > 0:
				if self.version[0] == "6":
					values = {"recordTime": markertime, "recordId": self.get_recording_id(room), "type": "simple", "message": markername}
				elif self.version[0] == "5":
					values = {"event": markername, "time": markertime, "color": color}
				data = self.send_to_valt(url, values=values)
				self.logger.info(__name__ + ": " + "Comment " + markername + " added in " + str(self.get_room_name(room)))
				return 1
			else:
				return 0

	def get_recording_time(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			is_recording = self.is_recording(room)
			if is_recording is not True:
				if is_recording is False:
					self.handle_error("No Recording")
				return 0
			url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				return data['data']['recording']['time']
			else:
				return 0

	def is_paused(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/' + str(room) + '/status?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if data['data']['status'] == 'paused':
					return True
				else:
					return False
			return 0

	def is_locked(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/' + str(room) + '/status?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if data['data']['status'] == 'locked':
					return True
				else:
					return False
			return 0

	def get_cameras(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			if room is not None and room != "" and room != "None":
				url = self.baseurl + 'admin/rooms/' + str(room) + '/cameras?access_token=' + self.accesstoken
				data = self.send_to_valt(url)
				if isinstance(data, dict):
					if data['data']['cameras']:
						return data['data']['cameras']
					else:
						self.handle_error("No Cameras")
						return 0
				else:
					self.handle_error("No Cameras")
					return 0
			else:
				self.handle_error("Invalid Room ID")
				return 0

	def get_room_name(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			if room is not None and room != "" and room != "None":
				url = self.baseurl + 'rooms/info/' + str(room) + '?access_token=' + self.accesstoken
				data = self.send_to_valt(url)
				if isinstance(data, dict):
					return data['data']['name']
				else:
					return 0
			else:
				return 0

	def get_room_status(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'rooms/' + str(room) + '/status?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if data['data']['status'] == 'available':
					return 1
				elif data['data']['status'] == 'recording':
					return 2
				elif data['data']['status'] == 'paused':
					return 3
				elif data['data']['status'] == 'locked':
					return 4
				elif data['data']['status'] == 'prepared':
					return 5
				else:
					self.handle_error("Unknown Status")
					return 0
			else:
				self.handle_error("Invalid Room ID")
				return 0

	def lock_room(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		room_status = self.get_room_status(room)
		if room_status == 1 or room_status == 5:
			url = self.baseurl + 'rooms/' + str(room) + '/lock' + '?access_token=' + self.accesstoken
			values = {"nothing": "nothing"}
			data = self.send_to_valt(url, values=values)
			self.logger.info(__name__ + ": " + str(self.get_room_name(room)) + " Locked")
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0
		else:
			self.handle_error("No Lock")
			return 0

	def unlock_room(self: VALT, room):
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		locked = self.is_locked(room)
		if locked is True:
			url = self.baseurl + 'rooms/' + str(room) + '/unlock' + '?access_token=' + self.accesstoken
			values = {"nothing": "nothing"}
			data = self.send_to_valt(url, values=values)
			self.logger.info(__name__ + ": " + str(self.get_room_name(room)) + " Unlocked")
			if isinstance(data, dict):
				return data['data']['id']
			else:
				return 0
		elif locked is False:
			self.handle_error("Not Locked")
			return 0
		else:
			return 0

	# ── Deprecated aliases ────────────────────────────────────────

	def isrecording(self: VALT, room):
		warnings.warn("isrecording is deprecated and will be removed in a future version. Use is_recording instead.", DeprecationWarning, stacklevel=2)
		return self.is_recording(room)

	def getrecordingid(self: VALT, room):
		warnings.warn("getrecordingid is deprecated and will be removed in a future version. Use get_recording_id instead.", DeprecationWarning, stacklevel=2)
		return self.get_recording_id(room)

	def startrecording(self: VALT, room, name, **kwargs):
		warnings.warn("startrecording is deprecated and will be removed in a future version. Use start_recording instead.", DeprecationWarning, stacklevel=2)
		return self.start_recording(room, name, **kwargs)

	def stoprecording(self: VALT, room):
		warnings.warn("stoprecording is deprecated and will be removed in a future version. Use stop_recording instead.", DeprecationWarning, stacklevel=2)
		return self.stop_recording(room)

	def pauserecording(self: VALT, room):
		warnings.warn("pauserecording is deprecated and will be removed in a future version. Use pause_recording instead.", DeprecationWarning, stacklevel=2)
		return self.pause_recording(room)

	def resumerecording(self: VALT, room):
		warnings.warn("resumerecording is deprecated and will be removed in a future version. Use resume_recording instead.", DeprecationWarning, stacklevel=2)
		return self.resume_recording(room)

	def addcomment(self: VALT, room, markername, color="red", **kwargs):
		warnings.warn("addcomment is deprecated and will be removed in a future version. Use add_comment instead.", DeprecationWarning, stacklevel=2)
		return self.add_comment(room, markername, color, **kwargs)

	def getrecordingtime(self: VALT, room):
		warnings.warn("getrecordingtime is deprecated and will be removed in a future version. Use get_recording_time instead.", DeprecationWarning, stacklevel=2)
		return self.get_recording_time(room)

	def ispaused(self: VALT, room):
		warnings.warn("ispaused is deprecated and will be removed in a future version. Use is_paused instead.", DeprecationWarning, stacklevel=2)
		return self.is_paused(room)

	def islocked(self: VALT, room):
		warnings.warn("islocked is deprecated and will be removed in a future version. Use is_locked instead.", DeprecationWarning, stacklevel=2)
		return self.is_locked(room)

	def getcameras(self: VALT, room):
		warnings.warn("getcameras is deprecated and will be removed in a future version. Use get_cameras instead.", DeprecationWarning, stacklevel=2)
		return self.get_cameras(room)

	def getroomname(self: VALT, room):
		warnings.warn("getroomname is deprecated and will be removed in a future version. Use get_room_name instead.", DeprecationWarning, stacklevel=2)
		return self.get_room_name(room)

	def getroomstatus(self: VALT, room):
		warnings.warn("getroomstatus is deprecated and will be removed in a future version. Use get_room_status instead.", DeprecationWarning, stacklevel=2)
		return self.get_room_status(room)

	def lockroom(self: VALT, room):
		warnings.warn("lockroom is deprecated and will be removed in a future version. Use lock_room instead.", DeprecationWarning, stacklevel=2)
		return self.lock_room(room)

	def unlockroom(self: VALT, room):
		warnings.warn("unlockroom is deprecated and will be removed in a future version. Use unlock_room instead.", DeprecationWarning, stacklevel=2)
		return self.unlock_room(room)
