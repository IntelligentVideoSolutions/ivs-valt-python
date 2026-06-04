from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtFilters:
	def get_filters(self: VALT):
		# Returns list of all filters or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'filters?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get filters")
			return 0

	def get_filter(self: VALT, filter_id):
		# Returns a filter dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'filters/{filter_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handleerror("Unable to get filter")
			return 0

	def get_filter_template_fields(self: VALT):
		# Returns list of template fields available for filtering or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'filters/template_fields?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data'].get('fields', data['data'])
		else:
			self.handleerror("Unable to get filter template fields")
			return 0

	def create_filter(self: VALT, name, **kwargs):
		# Creates a filter. Returns new filter id or 0 on failure.
		# Optional kwargs: fields, rooms, authors, date
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'filters?access_token={self.accesstoken}'
		values = {'name': name}
		for key in ('fields', 'rooms', 'authors', 'date'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created filter '{name}'")
			return data['data'].get('id', 0)
		else:
			self.handleerror("Unable to create filter")
			return 0

	def update_filter(self: VALT, filter_id, **kwargs):
		# Updates a filter. Returns filter id or 0 on failure.
		# Optional kwargs: name, fields, rooms, authors, date
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'filters/{filter_id}/edit?access_token={self.accesstoken}'
		values = {}
		for key in ('name', 'fields', 'rooms', 'authors', 'date'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated filter {filter_id}")
			return data['data'].get('id', 0)
		else:
			self.handleerror("Unable to update filter")
			return 0

	def delete_filter(self: VALT, filter_id):
		# Deletes a filter. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'filters/{filter_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted filter {filter_id}")
			return 1
		else:
			self.handleerror("Unable to delete filter")
			return 0
