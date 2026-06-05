from __future__ import annotations
from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
	from ..valt import VALT

class ValtUsers:
	def get_user_by_card_number(self: VALT, cardnumber):
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		if self.major_version == "5":
			return self.get_user_by_card_number_v5(cardnumber)
		elif self.major_version == "6":
			if int(self.minor_version) >= 5:
				return self.get_user_by_card_number_v6(cardnumber)
			else:
				return self.get_user_by_card_number_v5(cardnumber)
		else:
			self.logger.error(__name__ + ": Unable to Determine VALT version")
			return 0

	def get_user_by_card_number_v6(self: VALT, cardnumber):
		# Function returns user matching card number.
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/users' + '?access_token=' + self.accesstoken + '&cardNumber=' + str(cardnumber)
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				if data['data']:
					return data['data'][0]['id']
				else:
					self.logger.info(__name__ + ": " + "No user found with card number: " + str(cardnumber))
					return 0
			else:
				return 0

	def get_user_by_card_number_v5(self: VALT, cardnumber):
		# Function returns user matching card number.
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			user_list = self.get_users()
			found_user = None
			if isinstance(user_list, list):
				for user in user_list:
					if user['card_number'] == cardnumber:
						found_user = user['id']
				if found_user is not None:
					return found_user
				else:
					self.logger.info(__name__ + ": " + "No user found with card number: " + str(cardnumber))
					return 0
			else:
				self.logger.info(__name__ + ": " + "No user found with card number: " + str(cardnumber))
				return 0

	def get_user(self: VALT, user_id):
		# Returns full user dict or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/users/{user_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get user")
			return 0

	def create_user(self: VALT, name, password, **kwargs):
		# Creates a user. Returns new user id or 0 on failure.
		# Optional kwargs: display_name, user_group, card_number, rooms, video_access
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/users?access_token={self.accesstoken}'
		values = {'name': name, 'password': password}
		for key in ('display_name', 'user_group', 'card_number', 'rooms', 'video_access'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created user '{name}'")
			return data['data'].get('id', 0)
		else:
			self.handle_error("Unable to create user")
			return 0

	def delete_user(self: VALT, user_id):
		# Deletes a user. Returns 1 on success or 0 on failure.
		if not self.connected:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/users/{user_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted user {user_id}")
			return 1
		else:
			self.handle_error("Unable to delete user")
			return 0

	def update_user(self: VALT, user_id, **kwargs):
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/users/' + str(user_id) + '/edit?access_token=' + self.accesstoken
			data = self.send_to_valt(url, values=kwargs)
			if isinstance(data, dict):
				return data['data']
			else:
				return 0

	def get_users(self: VALT):
		# Function to return a list of users.
		# Returns 0 on failure.
		# Each list item is a dictionary with information about the user.
		if not self.connected:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
			return 0
		else:
			url = self.baseurl + 'admin/users?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if isinstance(data, dict):
				return data['data']
			else:
				self.handle_error("No Users")
				return 0

	# ── Deprecated alias ─────────────────────────────────────────

	def getusers(self: VALT):
		warnings.warn("getusers is deprecated and will be removed in a future version. Use get_users instead.", DeprecationWarning, stacklevel=2)
		return self.get_users()
