from __future__ import annotations
from typing import TYPE_CHECKING

import logging

if TYPE_CHECKING:
	from ..valt import VALT

class valt_log:
	def __init__(self: VALT, **kwargs):
		super().__init__(**kwargs) # Passes arguments to the next class in MRO
		self.set_up_logging()
	def set_up_logging(self: VALT,logpath='valt.log'):
		if logging.getLogger("kivy").hasHandlers():
			self.logger = logging.getLogger("kivy").getChild(__name__)
		else:
			self.logger = logging.getLogger(__name__)
			# logging.basicConfig(filename=logpath, level=logging.DEBUG)
			logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler(logpath), logging.StreamHandler()])

	def log_level(self: VALT, loglevel):
		# Standardize input to lowercase for consistency
		match loglevel.lower():
			case "debug":
				self.logger.setLevel(logging.DEBUG)
			case "info":
				self.logger.setLevel(logging.INFO)
			case "warn" | "warning":
				self.logger.setLevel(logging.WARNING)
			case "error":
				self.logger.setLevel(logging.ERROR)
			case "critical":
				self.logger.setLevel(logging.CRITICAL)
			case _:
				self.logger.info(f"Invalid log level '{loglevel}' provided. Defaulting to INFO.")
				self.logger.setLevel(logging.INFO)
