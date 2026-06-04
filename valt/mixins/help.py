from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtHelp:
	def get_helps(self: VALT):
		# Returns list of all help items or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'help?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('helps', data['data'])
		else:
			self.handle_error("Unable to get helps")
			return 0

	def get_help(self: VALT, help_id):
		# Returns a help dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'help/{help_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get help")
			return 0

	def create_help(self: VALT, title, content):
		# Creates a help item. Returns the created help dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'help?access_token={self.accesstoken}'
		values = {'title': title, 'content': content}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created help '{title}'")
			return data['data']
		else:
			self.handle_error("Unable to create help")
			return 0

	def update_help(self: VALT, help_id, title, content):
		# Updates a help item. Returns help id or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'help/{help_id}/edit?access_token={self.accesstoken}'
		values = {'title': title, 'content': content}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated help {help_id}")
			return data['data'].get('id', 0)
		else:
			self.handle_error("Unable to update help")
			return 0

	def delete_help(self: VALT, help_id):
		# Deletes a help item. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'help/{help_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted help {help_id}")
			return 1
		else:
			self.handle_error("Unable to delete help")
			return 0
