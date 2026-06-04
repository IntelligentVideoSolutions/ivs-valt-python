from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..valt import VALT

class ValtTemplate:
	def get_templates(self: VALT, template_type):
		# Returns dict with 'templates' list and 'default' template id on success, 0 on failure.
		# template_type must be one of: 'comment', 'info', 'marker'
		if self.accesstoken == 0:
			self.logger.error(__name__ + ": Not Currently Authenticated to VALT")
			return 0

		url = self.baseurl + f'template?type={template_type}&access_token={self.accesstoken}'
		data = self.send_to_valt(url)
		if isinstance(data, dict) and 'templates' in data:
			return data
		else:
			self.handle_error("Unable to get templates")
			return 0
