class valt_preset:
	def get_camera_presets(self, camera_id):
		# Function to retrieve presets for a given camera.
		# Returns a list of preset dicts or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'presets/{camera_id}?access_token=' + self.accesstoken
		data = self.send_to_valt(url)
		if isinstance(data, list):
			return data
		else:
			self.handleerror("Unable to get camera presets")
			return 0


	def create_camera_preset(self, camera_id, name):
		# Function to create a new preset for a given camera.
		# Returns preset ID or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'presets/{camera_id}/add?access_token=' + self.accesstoken
		values = {"name": name}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'id' in data:
			self.logger.info(__name__ + f": Preset '{name}' created for camera {camera_id}")
			return data['id']
		else:
			self.handleerror("Unable to create preset")
			return 0

	def apply_camera_preset(self, camera_id, preset_id):
		# Function to apply an existing preset to a given camera.
		# Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'presets/{camera_id}/apply?access_token=' + self.accesstoken
		values = {"preset": preset_id}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'message' in data:
			self.logger.info(__name__ + f": Preset {preset_id} applied to camera {camera_id}")
			return 1
		else:
			self.handleerror("Unable to apply preset")
			return 0

	def delete_camera_preset(self, camera_id, preset_id):
		# Function to delete an existing preset from a given camera.
		# Returns deleted preset ID or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'presets/{camera_id}/delete?access_token=' + self.accesstoken
		values = {"preset": preset_id}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'id' in data:
			self.logger.info(__name__ + f": Preset {preset_id} deleted from camera {camera_id}")
			return data['id']
		else:
			self.handleerror("Unable to delete preset")
			return 0