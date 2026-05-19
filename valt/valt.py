from .mixins.admin import valt_admin
from .mixins.comment import valt_comment
from .mixins.communication import valt_communication
from .mixins.errors import valt_errors
from .mixins.groups import valt_groups
from .mixins.log import valt_log
from .mixins.monitor import valt_monitor
from .mixins.preset import valt_preset
from .mixins.recording import valt_recording
from .mixins.room import valt_room
from .mixins.users import valt_users
from .mixins.auth import valt_auth

class VALT(valt_communication,valt_log,valt_recording,valt_room,valt_preset,valt_users,valt_groups,valt_comment,valt_admin,valt_errors,valt_auth,valt_monitor):
	def __init__(self, valt_address, valt_username, valt_password, timeout=5,logpath="ivs.log", **kwargs):
		super().__init__()
		if valt_address != "None" and valt_address != "" and valt_address is not None:
			if valt_address.find("http", 0, 4) == -1:
				self.baseurl = 'http://' + valt_address + '/api/v3/'
			else:
				self.baseurl = valt_address + '/api/v3/'
		else:
			self.baseurl = None
		self.username = valt_username
		self.password = valt_password
		self.success_reauth_time = 28800
		self.failure_reauth_time = 30
		self.logpath = logpath
		self._errormsg_observers = []
		self._errormsg = None
		self.testmsg = None
		self._accesstoken = 0
		self._accesstoken_observers = []
		self.httptimeout = int(timeout)
		self.kill_threads = False
		self.auth()
		self._selected_room_status = 99

		self.run_check_room_status = False
		self._observers =  []

		if 'room' in kwargs:
			try:
				self.selected_room = int(kwargs['room'])
			except:
				self.selected_room = None
		else:
			self.selected_room = None

		if 'room_check_interval' in kwargs:
			self.room_check_interval = int(kwargs['room_check_interval'])
		else:
			self.room_check_interval = 5

		self.start_room_check_thread()

	def disconnect(self):
		self.kill_threads = True

	def change_timeout(self,new_timeout):
		self.logger.info(__name__ + ": " + "HTTP Timeout set to " + str(new_timeout))
		self.httptimeout = int(new_timeout)



