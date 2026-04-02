class valt_comment:
	def get_comments_by_record(self, record_id):
		# Function to return a list of all comments associated with a specific recording
		# Returns list of comment dictionaries on success
		# Returns 0 on failure
		# Added by AI
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + 'comment/record/' + str(record_id) + '?access_token=' + self.accesstoken
		data = self.send_to_valt(url)

		if type(data).__name__ == "list":
			return data
		else:
			self.logger.error(__name__ + ": " + "Unable to retrieve comments for record " + str(record_id))
			return 0

	def create_comment(self, comment_data):
		# Created by AI – Function to create a new comment in VALT.
		# Expects comment_data as a dict.
		# Returns the created comment dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + 'comment?access_token=' + self.accesstoken
		data = self.send_to_valt(url, values=comment_data)

		if isinstance(data, dict):
			self.logger.info(__name__ + f": Created comment on record {comment_data.get('recordId', 'unknown')}")
			return data.get('data')
		else:
			self.handleerror("Unable to create comment")
			return 0

	def update_comment(self, comment_id, update_data):
		# Created by AI – Function to update an existing comment in VALT.
		# Returns the updated comment dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'comment/update/{comment_id}?access_token=' + self.accesstoken
		data = self.send_to_valt(url, values=update_data)

		if isinstance(data, dict):
			self.logger.info(__name__ + f": Updated comment ID {comment_id}")
			return data.get('data')
		else:
			self.handleerror("Unable to update comment")
			return 0

	def delete_comment(self, comment_id):
		# Created by AI – Function to delete a comment by ID in VALT.
		# Returns comment ID on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'comment/{comment_id}?access_token=' + self.accesstoken
		try:
			request = urllib.request.Request(url, method='DELETE')
			response = urllib.request.urlopen(request, timeout=self.httptimeout)
			result = json.load(response)
			self.logger.info(__name__ + f": Deleted comment ID {comment_id}")
			return result.get('id', 0)
		except Exception as e:
			self.logger.error(__name__ + ": Failed to delete comment")
			self.handleerror(e)
			return 0

	def download_comment_file(self, comment_id, output_path):
		# Created by AI – Function to download a comment's attached file to a local path.
		# Returns True on success, False on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return False

		url = self.baseurl + f'comment/{comment_id}/file?access_token=' + self.accesstoken
		try:
			req = urllib.request.Request(url)
			with urllib.request.urlopen(req, timeout=self.httptimeout) as response, open(output_path, 'wb') as out_file:
				out_file.write(response.read())
			self.logger.info(__name__ + f": File for comment {comment_id} saved to {output_path}")
			return True
		except Exception as e:
			self.logger.error(__name__ + ": Failed to download comment file")
			self.handleerror(e)
			return False
