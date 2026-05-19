from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class valt_users:
	def get_user_by_card_number(self: VALT, cardnumber):
		if self.major_version == "5":
			return self.get_user_by_card_number_v5(cardnumber)
		elif self.major_version == "6":
			if int(self.minor_version) >= 5:
				return self.get_user_by_card_number_v6(cardnumber)
			else:
				return self.get_user_by_card_number_v5(cardnumber)
	def get_user_by_card_number_v6(self: VALT, cardnumber):
		# Function returns user matching card number.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'admin/users' + '?access_token=' + self.accesstoken + '&cardNumber=' + str(cardnumber)
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				if data['data']:
					return data['data'][0]['id']
				else:
					self.logger.info(__name__ + ": " + "No user found with card number: " + str(cardnumber))
					return 0
	def get_user_by_card_number_v5(self: VALT, cardnumber):
		# Function returns user matching card number.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			user_list = self.getusers()
			found_user = None
			if type(user_list).__name__ == "list":
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
	def update_user(self: VALT,**kwargs):
		pass

	def getusers(self: VALT):
		# Function to return a list of users.
		# Returns 0 on failure.
		# Each list item is a dictionary with information about the user.		if self.accesstoken == 0:
			self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
		else:
			url = self.baseurl + 'admin/users?access_token=' + self.accesstoken
			data = self.send_to_valt(url)
			if type(data).__name__ == "dict":
				return data['data']
			else:
				self.handleerror("No Users")
				return 0
