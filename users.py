class valt_users:
	def get_user_by_card_number(self, cardnumber):
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
	def update_user(self,**kwargs):
		pass