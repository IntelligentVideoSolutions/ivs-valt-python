from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtAdminTemplates:
	def get_admin_templates(self: VALT):
		# Returns list of all admin templates or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get admin templates")
			return 0

	def get_admin_template(self: VALT, template_id):
		# Returns a template dict or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get admin template")
			return 0

	def create_admin_template(self: VALT, name, template_type, entity_name, **kwargs):
		# Creates a template. Returns new template id or 0 on failure.
		# Optional kwargs: hidden, fields
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates?access_token={self.accesstoken}'
		values = {'name': name, 'type': template_type, 'entity_name': entity_name}
		for key in ('hidden', 'fields'):
			if key in kwargs:
				values[key] = kwargs[key]
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Created template '{name}'")
			return data['data'].get('id', 0)
		else:
			self.handle_error("Unable to create admin template")
			return 0

	def update_admin_template(self: VALT, template_id, **kwargs):
		# Updates a template. Returns template id or 0 on failure.
		# Optional kwargs: name, type, hidden, entity_name, fields
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}/edit?access_token={self.accesstoken}'
		values = {k: v for k, v in kwargs.items()}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated template {template_id}")
			return data['data'].get('id', 0)
		else:
			self.handle_error("Unable to update admin template")
			return 0

	def delete_admin_template(self: VALT, template_id):
		# Deletes a template. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted template {template_id}")
			return 1
		else:
			self.handle_error("Unable to delete admin template")
			return 0

	def get_template_fields(self: VALT, template_id):
		# Returns list of fields for a template or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}/fields?access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'data' in data:
			return data['data']
		else:
			self.handle_error("Unable to get template fields")
			return 0

	def add_template_fields(self: VALT, template_id, fields):
		# Adds fields to a template. fields is a list of field dicts.
		# Returns list of new field ids or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}/fields?access_token={self.accesstoken}'
		values = {'fields': fields}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Added fields to template {template_id}")
			return data['data'].get('fields', data['data'])
		else:
			self.handle_error("Unable to add template fields")
			return 0

	def update_template_field(self: VALT, template_id, field_id, **kwargs):
		# Updates a template field. Returns field dict or 0 on failure.
		# Optional kwargs: on, required, type, name, data
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}/fields/{field_id}/edit?access_token={self.accesstoken}'
		values = {k: v for k, v in kwargs.items()}
		data = self.send_to_valt(url, values=values)
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Updated field {field_id} on template {template_id}")
			return data['data']
		else:
			self.handle_error("Unable to update template field")
			return 0

	def delete_template_field(self: VALT, template_id, field_id):
		# Deletes a template field. Returns 1 on success or 0 on failure.
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0
		url = self.baseurl + f'admin/templates/{template_id}/fields/{field_id}/delete?access_token={self.accesstoken}'
		data = self.send_to_valt(url, values={})
		if isinstance(data, dict) and 'data' in data:
			self.logger.info(__name__ + f": Deleted field {field_id} from template {template_id}")
			return 1
		else:
			self.handle_error("Unable to delete template field")
			return 0
